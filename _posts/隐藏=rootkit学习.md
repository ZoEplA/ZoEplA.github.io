---
layout: post
title:  Rootkit学习
categories: 学习笔记
tags: tools
mathjax: true
abbrlink: 49621
date: 2020-10-28 11:00:00
---


Rootkit 是一种特殊的恶意软件，它的功能是在安装目标上隐藏自身及指定的文件、进程和网络连接（端口）等信息，比较多见到的是 Rootkit 一般都和木马、后门等其他恶意程序结合使用。
RootKit 分为用户态rootkit 和内核级 rootkit。内核级 rootkit 可分基于 LKM 的 rootkit（又细分为系统调用表修改类以及VFS层rootkit等）和非 LKM 的 rootkit（如 patch kernel等）。

Rootkit实现环境：Ubuntu20.04，kernel 版本为5.4.52

Rootkit工具简介：本工具主要为基于 LKM 实现的，包括使用  vfs  层隐藏文件和端口、进程摘链、模块摘链等原理，单独维持隐藏链表达到一次可隐藏多个文件、进程等效果，通过实现在系统调用表中 hook openat 系统调用来整合 rootkit 功能到 cat 命令中（plusls大佬实现的工具）。



### 文件隐藏

目的：为了辅助其他恶意程序,例如木马等，rootkit可以对这些特定文件进行隐藏。
实现功能：支持隐藏系统内所有文件，并支持隐藏多个文件。

原理：基于hook Virtual file systems (VFS) 层的函数到我们定义的fake函数来过滤特定文件信息，这里是filldir函数。

通过 strace ls 来查看文件遍历的实现，也就是系统调用，这里是 getdents64() 函数，getdents64 函数主要用于获取内容返回，如果找到其返回值在哪，就可以对该返回值进行过滤操作来隐藏特定文件。

![Alt text](/images/posts/rootkit/1603783899101.png)

查看 getdents 的源码，我们可以发现其调用链为：
```
sys_getdents --> iterate_dir --> iterate_shared(在 struct file_operations里, 注：高版本内核从 iterate 改进为 iterate_share，可以在同一个目录同时进行多个调用) --> ……--> struct dir_context.actor(filldir)
//iterate_share是可以用来实现并行访问同一个目录和文件的结构体
```
filldir函数：负责把一项记录(比如说目录下的一个文件或者一个子目录)填到返回的缓冲区里

因此我们只需要hook filldir函数，过滤特定文件或者目录阻止其返回缓冲区。如下图所示：

![Alt text](/images/posts/rootkit/1603784243552.png)

这里通过node号码ino来进行对比，过滤特定文件或目录，阻止对应信息返回缓冲区。

### 进程隐藏

这里有两种方法，第一种可以使用与文件隐藏一样的hook方法隐藏proc下的对应pid的文件内容。因为Linux下万物皆文件，而ps显示进程原理是通过对/proc下的进行枚举，发现存在的目录，所以隐藏文件的原理一样可以用于此。

实现过程：对隐藏文件模块中加入条件判断，若需要隐藏的进程号吻合则直接返回，不经过写缓冲区函数


![Alt text](/images/posts/rootkit/1603784361668.png)

但是这种方法很容易被检测到，只需要遍历从1到PID_MAX发送SIG信号，比如说`kill -20 pid`，去检测该进程是否存在，如果存在则可发现隐藏进程。

![Alt text](/images/posts/rootkit/1603785349294.png)

因为系统通过` task_struct `结构体拿到进程信息（感知存在），会调用api 索引查找关系 ：`pid_num->pid->task_struct`；pid 与相关` task_struct `通过双向链表tasks连接；内核同时维护一条全局` tastlist `双向循环链表；调用链访问这些上述结构体并返回信息，所以只需要对全局链表`tasklist`和`pid`链表进行摘链即可。

```
//pid调用链
proc_pid_readdir -> next_tgid ->  find_ge_pid -> pid_task -> hlist_entry
```

![Alt text](/images/posts/rootkit/1603785506560.png)

而ubuntu20.04的新版本kernel取消了通过hash链表来进行寻找，而是使用红黑树来进行寻找，提高效率


### 端口隐藏

端口隐藏也有两个方法，隐藏第一种`hook`方法，是跟前面的`hook`一样，只是这里`netstat`是通过查看`/proc/net/tcp`等序列文件来获取端口信息，而序列文件有四种操作，这里我们只需要hook他的show函数即可，然后过滤buf中的内容来过滤端口信息。

![Alt text](/images/posts/rootkit/1603787693879.png)

![Alt text](/images/posts/rootkit/1603787723219.png)

而这里有个问题，就是新版本的Linux里现在都使用`ss -ntpl`来获取端口信息，而不会走读取`/proc/net/tcp`文件这个调用链，那我们前面的hook做法就是失效。

![Alt text](/images/posts/rootkit/1603788106735.png)

我们可以`Hook recvmsg` 函数返回端口信息，然后对比遍历 `nlmsghdr` 结构体以过滤端口从而达到隐藏端口的目的。

这里还存在一个检测问题就是如果检测端口是否占用的方法即可检测出隐藏端口，我们可以hook sys_bind函数过滤报错信息为return 0（即返回bind成功），也就是你bind了一个假的端口而已。

### ko模块隐藏
目的： Linux内核模块在加载到系统后的相关信息可以被用户获取。为了实现其隐蔽性，需要对Rootkit模块进行隐藏。
原理：主要通过摘链的方法把模块隐藏。

用户态下查看模块的方式（两种方法）：
+ lsmod(读取/proc/modules文件实现)
+ 查看/proc/modules文件
+ 查看/sys/module目录

![Alt text](/images/posts/rootkit/1603791693713.png)

/proc/modules文件中的模块信息是利用struct modules结构体中的list_head链表来遍历获得。调用 `list_del_init(&__this_module.list);`可以直接从摘链实现从全局链表中删除模块信息，原理如下的源码分析；

/sys/module目录下存放着当前加载的所有模块的信息，这些信息存放在kobject结构体中， sysfs与kobject紧密相连，可以看作是Linux设备模型的基础，一般内嵌在其他结构体来发挥作用。即：一个kobject对象对应其中一个目录或者文件。同样我们可以通过`kobject_del(&__this_module.mkobj.kobj);`实现从kobject链表中摘除自己，kobject_del会删除对应的模块目录以及所有子目录。（缺点：计数变为-2，难以恢复）

del调用顺序：
`list_del_init(&__this_module.list);`
```

static inline void list_del_init(struct list_head *entry)
{
	__list_del_entry(entry);//unlink操作，将前后模块连接起来
	INIT_LIST_HEAD(entry); //entry->next = entry; entry->prev = entry; 模块指针指向自己
}

static inline void __list_del_entry(struct list_head *entry)
{
	__list_del(entry->prev, entry->next);
}

static inline void __list_del(struct list_head * prev, struct list_head * next)
{
	next->prev = prev; // 做unlink操作，设置next的前一个是prev
	WRITE_ONCE(prev->next, next); //prev->next = next; unlink操作2，设置prev的后一个是next
}

static inline void INIT_LIST_HEAD(struct list_head *list)
{
	list->next = list;
	list->prev = list;
}
```

`kobject_del(&__this_module.mkobj.kobj);`
```
/**
 * kobject_del() - Unlink kobject from hierarchy. <从层次结构取消链接kobject>
 * @kobj: object.
 *
 * This is the function that should be called to delete an object
 * successfully added via kobject_add().<删除通过kobject_add()添加的对象时应调用此函数。>
 */
void kobject_del(struct kobject *kobj)
{
	struct kernfs_node *sd;
	const struct kobj_type *ktype;

	if (!kobj)
		return;

	sd = kobj->sd;
	ktype = get_ktype(kobj);

	if (ktype)
		sysfs_remove_groups(kobj, ktype->default_groups);

	sysfs_remove_dir(kobj);
	sysfs_put(sd);

	kobj->state_in_sysfs = 0;
	kobj_kset_leave(kobj);
	kobject_put(kobj->parent);
	kobj->parent = NULL;
}
```



### 提权

![Alt text](/images/posts/rootkit/1603791373677.png)


### sys_call_table

这里hook `sys_call_table`要先找到`sys_call_table`的地址，然后关闭写保护，接着改写`sys_call_table`里面对应的函数指针，修改，最后开启写保护并返回。举个例子

```
real_sys_call_table = (void *)kallsyms_lookup_name("sys_call_table"); // 找到sys_call_table的地址

//修改sys_call_table的openat，hook cat命令
real_sys_openat = (void *)real_sys_call_table[__NR_openat];// 保存真实的sys_openat地址
disable_wp();//关闭写保护
real_sys_call_table[__NR_openat] = (void *)my_sys_openat;//修改函数指针为fake函数地址
enable_wp();//打开写保护

//恢复sys_call_table的openat函数指针
disable_wp();
real_sys_call_table[__NR_openat] = (void *)real_sys_openat; 
enable_wp();

inline void mywrite_cr0(unsigned long cr0)
{
    asm volatile("mov %0,%%cr0"
                 : "+r"(cr0), "+m"(__force_order));
}

void enable_wp(void)
{
    // 可能存在条件竞争
    unsigned long cr0;

    preempt_disable();
    cr0 = read_cr0();
    set_bit(X86_CR0_WP_BIT, &cr0);
    mywrite_cr0(cr0);
    preempt_enable();

    return;
}

void disable_wp(void)
{
    // 可能存在条件竞争
    unsigned long cr0;

    preempt_disable();
    cr0 = read_cr0();
    clear_bit(X86_CR0_WP_BIT, &cr0);
    mywrite_cr0(cr0);
    preempt_enable();

    return;
}
```


### 工具源码

大佬实现的工具源码：https://github.com/plusls/rootkit
