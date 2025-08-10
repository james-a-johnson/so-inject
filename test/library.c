#include "library.h"
#include <stdio.h>

int do_thing(void) {
    printf("doing thing\n");
    return 12;
}

static __attribute__((constructor)) void foo_bar() {
    printf("I got constructed\n");
}
