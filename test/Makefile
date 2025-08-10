all: liblib.so main inject.so

.PHONY: clean

RPATH=$(shell pwd)

liblib.so: library.c library.h
	clang -g -fPIC -rdynamic -shared -o liblib.so library.c


main: main.c liblib.so
	clang -g -o main main.c -L . -llib -Wl,-rpath $(RPATH)


inject.so: inject.asm
	nasm -f elf64 -o inject.o inject.asm
	ld -shared -PIC -o inject.so inject.o


clean:
	rm -f liblib.so
	rm -f main
	rm -f inject.so inject.o
