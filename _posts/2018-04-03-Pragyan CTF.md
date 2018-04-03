---
layout: post
title: "Pragyan CTF"
date: 2018-04-03 
categories: jekyll update
---
### Pragyan CTF
#### reversing50
直接IDA打开查看main函数，就是把十六进制转为char形式，flag就出来了

![image](/images/posts/Pragyan CTF/1520141353979.png)

#### pwn200

首先IDA载入看一下：

![image](/images/posts/Pragyan CTF/1520141419663.png)

看到密码；运行一下

![image](/images/posts/Pragyan CTF/1520141459758.png)

看到有flag，输入看一下，但是没有权限看，回去IDA看下函数

![image](/images/posts/Pragyan CTF/1520141514009.png)

有个flag.txt文件，还有一个函数可以读这个文件，但是因为文件长度要36字节，而flag.txt只有6字节

![image](/images/posts/Pragyan CTF/1520141589934.png)

考虑栈溢出，先是在选项那里溢出，怎样确保文件名是36个字节同时可以正常读取文件，给出提示：`Path Traversals are always a classic.`想到路径，所以弄成`././././././././././././././flag.txt`（也可以`.///////////////////////////flag.txt`；特别感谢某位大佬指点）， 然后这个解决了；
原来想在选项那里溢出，如图，后来发现栈里面在输入密码s1的下一个就是v9；所以直接在输入密码那里进行栈溢出，这样简单一点，其实在选项溢出也可以；

![image](/images/posts/Pragyan CTF/1520145157995.png)

还有一个突破点，一开始是在选项那里选1-7然后修改寄存器的值来修改文件名，一直有一部分不可控；后来知道直接选择非1-7就直接是一个未知的文件名，这样子我们覆盖的文件名就不会被重写了，他也没有检查文件序号，直接退出，这样子题目就引刃而解了；

在s1溢出到v9；同时注意到s1是16字节，而密码只有10字节，所以需要填充6个a，构造payload：`kaiokenx20aaaaaa././././././././././././././flag.txt`或者`kaiokenx20aaaaaa.///////////////////////////flag.txt`；然后选择8，得到flag：

![image](/images/posts/Pragyan CTF/1520145641674.png)

![image](/images/posts/Pragyan CTF/1520145659031.png)

flag：pctf{bUff3r-0v3Rfl0wS`4r3.alw4ys-4_cl4SsiC}

