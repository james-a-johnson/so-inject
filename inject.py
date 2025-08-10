import lief
from lief.ELF import Binary
import argparse


def do_injection(library: Binary, obj: Binary, export: bool) -> Binary:
    """Add symbol and section to shared object

    :param library: Shared object to add hook to
    :param obj: Shared object that symbol comes from
    :param export: Set to True to add the hook symbol as an exported function to the shared object

    Somewhat taken from https://lief.re//doc/latest/tutorials/04_elf_hooking.html"""
    # Get the actual symbol from the object file and make sure it exists
    sym = obj.get_symbol("_hook")
    hook_fixup = obj.get_symbol("hooked_constructor")
    if not sym:
        raise ValueError("Symbol '_hook' not found")
    if not hook_fixup:
        raise ValueError("Hook fixup not found")

    # Get the segment that the symbol is in and add it to the shared object
    constructor_segment = obj.segment_from_virtual_address(sym.value)
    # Make segment rwx because the dynamic loader needs to update a relocation in the text section
    constructor_segment.flags = lief.ELF.Segment.FLAGS.from_value(7)
    new_segment = library.add(constructor_segment)

    hook_addr = (
        new_segment.virtual_address + sym.value - constructor_segment.virtual_address
    )
    hook_fixup_addr = (
        new_segment.virtual_address
        + hook_fixup.value
        - constructor_segment.virtual_address
    )

    if export:
        exported_sym = library.add_exported_function(hook_addr)
        exported_sym.name = sym.name

    constructors = library.get_section(".init_array")
    if not constructors:
        raise ValueError(f"Section '.init_array' not found")

    first_constructor = constructors.virtual_address
    for reloc in library.dynamic_relocations:
        if reloc.address == first_constructor:
            reloc.address = hook_fixup_addr
            break

    hook_reloc = lief.ELF.Relocation(
        first_constructor,
        lief.ELF.Relocation.TYPE.X86_64_RELATIVE,
        lief.ELF.Relocation.ENCODING.RELA,
    )
    hook_reloc.addend = new_segment.virtual_address + sym.value
    if export:
        hook_reloc.symbol = exported_sym

    library.add_dynamic_relocation(hook_reloc)

    return library


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "library", type=str, help="The name of the library to inject into"
    )
    parser.add_argument("injection", type=str, help="The name of the injection file")
    parser.add_argument(
        "entry", type=str, help="The name of the entry symbol in the injection file"
    )
    parser.add_argument("output", type=str, help="The name of the output file")
    parser.add_argument("--export", action="store_true", help="Export injected symbols")
    args = parser.parse_args()

    library = lief.ELF.parse(args.library)
    if library is None:
        print(f"Could not parse {args.library} as an elf file")
    inject = lief.ELF.parse(args.injection)
    if inject is None:
        print(f"Could not parse {args.injection} as an elf file")

    new_so = do_injection(library, inject, args.export)
    new_so.write(args.output)


if __name__ == "__main__":
    main()
