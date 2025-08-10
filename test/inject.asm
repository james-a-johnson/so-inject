section .text
global hooked_constructor
global func:_hook

_hook:
        ; This could be required by the shared object and is a no-op when not supported
        endbr64

        mov rax, 1
        mov rdi, 1
        lea rsi, [rel message]
        mov rdx, end - message
        syscall

        ; Call the constructor that was overriden in the original binary
        call [rel hooked_constructor]

        ret


        align 8
hooked_constructor: db 0,0,0,0,0,0,0,0
message: db "You've been hooked!",0xa
end:
