# so-inject
Inject a new initialization function to a shared object.

This works by overwriting the first entry in the `.init_array` section to point to a different
symbol. So the first initialization function will be the injected function.

Only supports x86_64 shared objects.

See the files in `test` to get an idea of how it works. The `inject.asm` file gives the general
structure of how the hook needs to function. It must be an exported symbol called `_hook`. The
hook also needs to call a function pointer stored in `hooked_constructor` which must be another
exported symbol.

The entire hook function needs to live in the `.text` section. Only that section will be copied
into the new shared library. So keep all data and instructions in that one section. That section
will be marked as RWX in the final binary so you can have mutable data in that section.

The way that this works is that the text section of the injected binary will be copied to the
shared object and be marked as RWX. The first entry in the `.init_array` array will be updated
to be a relocation for the injected `_hook` function. The `hooked_constructor` value will
become a relocation for the function that was in the `.init_array`. With all of those changes,
the new shared object will work exactly the same as the original one but have whatever extra
behavior was added in the hook.
