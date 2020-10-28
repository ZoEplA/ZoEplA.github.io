---
layout: post
title:  Clang 学习（基于Clang的简单解释器编写）
categories: 学习笔记
tags: llvm
mathjax: true
abbrlink: 49621
date: 2020-10-28 00:00:00
---

## Clang 学习（基于Clang的简单解释器编写）

编译原理大作业---基于clang的解释器  

要求：实现一个基于Clang的基本解释器 

源码：https://github.com/ZoEplA/ast-interpreter 

### 参考资料

https://clang.llvm.org/doxygen/index.html

### 环境配置

这里使用源码编译，首先安装依赖库：

```
sudo apt install libz3-dev
sudo apt install z3
sudo apt install build-essential
sudo apt install cmake
apt install python-is-python3
# python-is-python3 这个我是去官网下载deb包安装的

```

开始编译：


cmake的部分编译选项解释
+ `CMAKE_C_COMPILER` : 告诉使用cmake哪个C编译器。默认情况下，它是`/usr/bin/cc`。
+ `CMAKE_CXX_COMPILER` ：告诉cmake要使用的C ++编译器。默认情况下，它是`/usr/bin/c++`
+ `CMAKE_C_FLAGS`：编译C文件时的选项，如-g；也可以通过add_definitions添加编译选项
+ `EXECUTABLE_OUTPUT_PATH` ：可执行文件的存放路径
+ `DLLVM_ENABLE_ASSERTIONS` : 启用断言检查进行编译（对于Debug版本，默认为Yes；对于所有其他版本，默认为No）
+ `DLLVM_TARGETS_TO_BUILD `: 将此设置为等于您要构建的目标, 可以将其设置为X86。可以在llvm-project/llvm/lib/Target目录中找到目标的完整列表。
+ `DCMAKE_INSTALL_PREFIX` : 为目录指定要在其中安装LLVM工具和库的完整路径名(默认/usr/local)
+ `LIBRARY_OUTPUT_PATH`：库文件路径
+ `CMAKE_BUILD_TYPE` ：告诉cmake要生成文件的构建类型。有效选项是Debug，Release，RelWithDebInfo和MinSizeRel。默认是 Debug，特点是编译时间大概需要数小时，占用空间大概15-20G，内存不足8G 的话大概会占用很多 swap 空间，造成速度更慢。改成 Release 省空间省时间，还不容易出错。
+ `DLLVM_ENABLE_RTTI=ON` : 打开LLVM的RTTI机制；这里解释一下编译选项`-DLLVM_ENABLE_RTTI=ON`和`-DLLVM_ENABLE_EH=ON`，由于LLVM使用自己的RTTI机制，在编译时默认禁用了C++的RTTI；同时，而LLVM的异常处理选项默认是关闭的，可以通过编译选项`-DLLVM_ENABLE_EH=ON`启用异常处理。
+ `DCLANG_ANALYZER_Z3_INSTALL_DIR`： z3的安装路径
+ `PYTHON_EXECUTABLE` :	通过将路径传递给Python解释器，强制CMake使用特定的Python版本。默认情况下，使用PATH中解释器的Python版本。
+ `LLVM_TARGETS_TO_BUILD` :	以分号分隔的列表控制将构建哪些目标并将其链接到llvm中。默认列表定义为`LLVM_ALL_TARGETS`，可以设置为包括树外目标。默认值包括： 。`AArch64, AMDGPU, ARM, BPF, Hexagon, Mips, MSP430, NVPTX, PowerPC, Sparc, SystemZ, X86, XCore`。
+ `LLVM_ENABLE_DOXYGEN`：从源代码构建基于doxygen的文档默认情况下，此功能处于禁用状态，因为它运行缓慢且会产生大量输出。
+ `LLVM_ENABLE_PROJECTS`:	以分号分隔的列表，用于选择要另外构建的其他LLVM子项目。（仅在使用并行项目布局（例如通过git）时有效）。默认列表为空。可以包括：`clang，libcxx，libcxxabi，libunwind，lldb，compiler-rt，lld，poly或debuginfo-tests`。
+ `LLVM_ENABLE_SPHINX` :	从源代码构建基于sphinx的文档。默认情况下禁用此选项，因为它速度慢并且会生成大量输出。推荐使用Sphinx 1.5或更高版本。
+ `LLVM_BUILD_LLVM_DYLIB`:	生成libLLVM.so。该库包含一组默认的LLVM组件，这些组件可以用覆盖`LLVM_DYLIB_COMPONENTS`。默认值包含大部分LLVM，并在中定义 `tools/llvm-shlib/CMakelists.txt`。该选项在Windows上不可用。
+ `LLVM_OPTIMIZED_TABLEGEN` :	构建在LLVM构建过程中使用的发布表生成, 这可以大大加快调试速度。

到官网下载源码，开始编译

```
sudo cmake /usr/local/src/llvm-10.0.0.src/ -DCMKAE_BUILD_TYPE=Release -DLLVM_ENABLE_ASSERTIONS=ON -DLLVM_TARGETS_TO_BUILD=X86 -DCMAKE_INSTALL_PREFIX=/usr/local/llvm10ra -DLLVM_ENABLE_RTTI=ON -DCLANG_ANALYZER_Z3_INSTALL_DIR=/usr/include/

# 运行串行构建会很慢,为了提高速度，请尝试运行并行构建。对于make，请使用-jNN选项，其中NN是并行作业的数量.
# 在这个过程中大部分的报错原因都是RAM不足，只能扩大磁盘内存，然后使用该-j标志对其进行限制降低即可；虚拟机编译的话出现这种情况居多。
sudo make -j4
sudo make install
```
扩大磁盘空间后还会报错，可能是swap空间不够了，可以尝试一下操作;(我最后用了120G磁盘空间、8G内存、2核、20G的swap终于装好了～)

**Swap 是 Linux 下的交换分区，类似 Windows 的虚拟内存**，当物理内存不足时，系统可把一些内存中不常用到的程序放入 Swap，解决物理内存不足的情况。但是如果开始使用 SWAP 的时候系统通常都会变得十分缓慢，因为硬盘 IO 占用的十分厉害，除非是 SSD 的情况下，速度才有可能稍微快一点。

```
# df 查看磁盘使用情况
sudo mkdir /swap
cd /swap
sudo swapoff swapfile # 停止扩充swap
sudo dd if=/dev/zero of=swapfile bs=1024 count=20000000 # 这里是20G，只要报错就往上调(我从2调到了20，当然应该12G差不多就够了我觉得
sudo mkswap -f swapfile # 
sudo swapon swapfile# 启动swapfile，让其生效
free -m # 查看当前内存使用情况以及swap空间情况
```


### 作业具体要求

![Alt text](/images/posts/clang/1602307869369.png)

![Alt text](/images/posts/clang/1602307893405.png)

### Clang的基本命令学习

通过一个例子来熟悉相关的命令与使用：

```
#include <stdio.h>

int main(){
        int a = 1;
        printf("%d",a);
        printf("test..");
        return 0;
}
```

#### Clang 的基本语法命令

| 命令      |     功能 |  
| :-------- | :--------| 
| -fmodules	    |  允许modules的语言特性 | 
| -fsyntax-only	    |  防止编译器生成代码,只是语法级别的说明和修改 | 
| -Xclang	    |  向clang编译器传递参数 | 
| -dump-tokens	    |  运行预处理器,拆分内部代码段为各种token | 
| -ast-dump	    |  构建抽象语法树AST,然后对其进行拆解和调试 | 
| -S	    |  只运行预处理和编译步骤 | 、
| -fobjc-arc	    |  为OC对象生成retain和release的调用 | 
| -emit-llvm	    |  允许modules的语言特性 | 
| -o     |  输出到目标文件 | 
| -c	    |  只运行预处理,编译和汇编步骤 | 

下面根据Clang的基本命令，学习编译器的基本流程的每一个步骤对

#### 预处理

```
clang-10 -E test.c
```
预处理顾名思义是预先处理。预处理的内容如下：头文件替换、macro 宏展开、处理其他的预编译指令。简单来说，“#” 这个符号是编译器预处理的标志。以下是简单c源码预处理之后的结果。

![Alt text](/images/posts/clang/1602338512970.png)

```
# 1 "test.c"
# 1 "<built-in>" 1
# 1 "<built-in>" 3
# 341 "<built-in>" 3
# 1 "<command line>" 1
# 1 "<built-in>" 2
# 1 "test.c" 2
# 1 "/usr/include/stdio.h" 1 3 4
# 27 "/usr/include/stdio.h" 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/libc-header-start.h" 1 3 4
# 33 "/usr/include/x86_64-linux-gnu/bits/libc-header-start.h" 3 4
# 1 "/usr/include/features.h" 1 3 4
# 439 "/usr/include/features.h" 3 4
# 1 "/usr/include/stdc-predef.h" 1 3 4
······
typedef __int8_t __int_least8_t;
typedef __uint8_t __uint_least8_t;
typedef __int16_t __int_least16_t;
typedef __uint16_t __uint_least16_t;
typedef __int32_t __int_least32_t;
typedef __uint32_t __uint_least32_t;
typedef __int64_t __int_least64_t;
typedef __uint64_t __uint_least64_t;
······
typedef struct
{
  int __count;
  union
  {
    unsigned int __wch;
    char __wchb[4];
  } __value;
} __mbstate_t;
# 6 "/usr/include/x86_64-linux-gnu/bits/types/__fpos_t.h" 2 3 4

typedef struct _G_fpos_t
{
  __off_t __pos;
  __mbstate_t __state;
} __fpos_t;
# 40 "/usr/include/stdio.h" 2 3 4
# 1 "/usr/include/x86_64-linux-gnu/bits/types/__fpos64_t.h" 1 3 4
# 10 "/usr/include/x86_64-linux-gnu/bits/types/__fpos64_t.h" 3 4
typedef struct _G_fpos64_t
{
  __off64_t __pos;
  __mbstate_t __state;
} __fpos64_t;
······
extern int fprintf (FILE *__restrict __stream,
      const char *__restrict __format, ...);
extern int printf (const char *__restrict __format, ...);
extern int sprintf (char *__restrict __s,
      const char *__restrict __format, ...) __attribute__ ((__nothrow__));
······
# 858 "/usr/include/stdio.h" 3 4
extern int __uflow (FILE *);
extern int __overflow (FILE *, int);
# 2 "test.c" 2

int main(){
 int a = 1;
 printf("%d",a);
 printf("test..");
 return 0;
}
```

#### Lexical Analysis - 词法分析（输出 token 流）

词法分析其实是编译器开始工作真正意义上的第一个步骤，其所做的工作主要为**将输入的代码转换为一系列符合特定语言的词法单元，这些词法单元类型包括了关键字、操作符、变量等等**。
词法分析，只需要将源代码以字符文本的形式转化成 Token 流的形式，不涉及校验语义，不需要递归，是线性的。

```
clang-10 -fmodules -fsyntax-only -Xclang -dump-tokens test.c
```

里面的每一行都可以说是一个 token 流。一个表达式也会被逐个的解析。

```
typedef 'typedef'        [StartOfLine]  Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stddef.h:46:1>
long 'long'      [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stddef.h:46:9 <Spelling=<built-in>:79:23>>
unsigned 'unsigned'      [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stddef.h:46:9 <Spelling=<built-in>:79:28>>
int 'int'        [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stddef.h:46:9 <Spelling=<built-in>:79:37>>
identifier 'size_t'      [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stddef.h:46:23>
semi ';'                Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stddef.h:46:29>
typedef 'typedef'        [StartOfLine]  Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:14:1>
identifier '__builtin_va_list'   [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:14:9>
identifier 'va_list'     [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:14:27>
semi ';'                Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:14:34>
typedef 'typedef'        [StartOfLine]  Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:32:1>
identifier '__builtin_va_list'   [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:32:9>
identifier '__gnuc_va_list'      [LeadingSpace] Loc=</usr/local/llvm10ra/lib/clang/10.0.0/include/stdarg.h:32:27>
······
r_paren ')'      [LeadingSpace] Loc=</usr/include/stdio.h:279:53 <Spelling=/usr/include/x86_64-linux-gnu/sys/cdefs.h:55:53>>
r_paren ')'             Loc=</usr/include/stdio.h:279:53 <Spelling=/usr/include/x86_64-linux-gnu/sys/cdefs.h:55:54>>
semi ';'         [LeadingSpace] Loc=</usr/include/stdio.h:279:66>
extern 'extern'  [StartOfLine]  Loc=</usr/include/stdio.h:292:1>
identifier 'FILE'        [LeadingSpace] Loc=</usr/include/stdio.h:292:8>
star '*'         [LeadingSpace] Loc=</usr/include/stdio.h:292:13>
identifier 'fmemopen'           Loc=</usr/include/stdio.h:292:14>
l_paren '('      [LeadingSpace] Loc=</usr/include/stdio.h:292:23>
void 'void'             Loc=</usr/include/stdio.h:292:24>
star '*'         [LeadingSpace] Loc=</usr/include/stdio.h:292:29>
identifier '__s'                Loc=</usr/include/stdio.h:292:30>
comma ','               Loc=</usr/include/stdio.h:292:33>
identifier 'size_t'      [LeadingSpace] Loc=</usr/include/stdio.h:292:35>
identifier '__len'       [LeadingSpace] Loc=</usr/include/stdio.h:292:42>
comma ','               Loc=</usr/include/stdio.h:292:47>
const 'const'    [LeadingSpace] Loc=</usr/include/stdio.h:292:49>
char 'char'      [LeadingSpace] Loc=</usr/include/stdio.h:292:55>
star '*'         [LeadingSpace] Loc=</usr/include/stdio.h:292:60>
identifier '__modes'            Loc=</usr/include/stdio.h:292:61>
······
r_paren ')'             Loc=</usr/include/stdio.h:859:35>
semi ';'                Loc=</usr/include/stdio.h:859:36>
int 'int'        [StartOfLine]  Loc=<test.c:3:1>
identifier 'main'        [LeadingSpace] Loc=<test.c:3:5>
l_paren '('             Loc=<test.c:3:9>
r_paren ')'             Loc=<test.c:3:10>
l_brace '{'             Loc=<test.c:3:11>
int 'int'        [StartOfLine] [LeadingSpace]   Loc=<test.c:4:2>
identifier 'a'   [LeadingSpace] Loc=<test.c:4:6>
equal '='        [LeadingSpace] Loc=<test.c:4:8>
numeric_constant '1'     [LeadingSpace] Loc=<test.c:4:10>
semi ';'                Loc=<test.c:4:11>
identifier 'printf'      [StartOfLine] [LeadingSpace]   Loc=<test.c:5:2>
l_paren '('             Loc=<test.c:5:8>
string_literal '"%d"'           Loc=<test.c:5:9>
comma ','               Loc=<test.c:5:13>
identifier 'a'          Loc=<test.c:5:14>
r_paren ')'             Loc=<test.c:5:15>
semi ';'                Loc=<test.c:5:16>
identifier 'printf'      [StartOfLine] [LeadingSpace]   Loc=<test.c:6:2>
l_paren '('             Loc=<test.c:6:8>
string_literal '"test.."'               Loc=<test.c:6:9>
r_paren ')'             Loc=<test.c:6:17>
semi ';'                Loc=<test.c:6:18>
return 'return'  [StartOfLine] [LeadingSpace]   Loc=<test.c:7:2>
numeric_constant '0'     [LeadingSpace] Loc=<test.c:7:9>
semi ';'                Loc=<test.c:7:10>
r_brace '}'      [StartOfLine]  Loc=<test.c:8:1>
eof ''          Loc=<test.c:8:2>
```

#### Semantic Analysis - 语法分析（输出(AST)抽象语法树）

```
#打印 AST 树
clang-10 –c -Xclang –ast-dump test.c
clang-10 -fmodules -fsyntax-only -Xclang -ast-dump test.c
```

```
#语法检查 clang-10 test.c -fsyntax-only 
#生成 LLVM 字节码 clang -c -emit-llvm test.c 
``` 

+ 语法分析的最终产物是输出抽象语法树（AST）
+ 语法分析在 Clang 中由 Parser 和 Sema 两个模块配合完成
+ 校验语法是否正确
+ 根据当前语言的语法，生成语意节点，并将所有节点组合成抽象语法树（AST）
+ 这一步跟源码等价，可以反写出源码
+ Static Analysis 静态分析
 + 通过语法树进行代码静态分析，找出非语法性错误
 + 模拟代码执行路径，分析出 control-flow graph(CFG) 【MRC时代会分析出引用计数的错误】
 + 预置了常用 Checker（检查器）

打印的语法树如下：

```
·······
|-FunctionDecl 0x55ce0579fa90 </usr/include/stdio.h:844:1, /usr/include/x86_64-linux-gnu/sys/cdefs.h:55:54> /usr/include/stdio.h:844:12 ftrylockfile 'int (FILE *)' extern
| |-ParmVarDecl 0x55ce0579f9f8 <col:26, col:32> col:32 __stream 'FILE *'
| `-NoThrowAttr 0x55ce0579fb38 </usr/include/x86_64-linux-gnu/sys/cdefs.h:55:35>
|-FunctionDecl 0x55ce0579fc30 </usr/include/stdio.h:847:1, /usr/include/x86_64-linux-gnu/sys/cdefs.h:55:54> /usr/include/stdio.h:847:13 funlockfile 'void (FILE *)' extern
| |-ParmVarDecl 0x55ce0579fba0 <col:26, col:32> col:32 __stream 'FILE *'
| `-NoThrowAttr 0x55ce0579fcd8 </usr/include/x86_64-linux-gnu/sys/cdefs.h:55:35>
|-FunctionDecl 0x55ce057a0370 </usr/include/stdio.h:858:1, col:27> col:12 __uflow 'int (FILE *)' extern
| `-ParmVarDecl 0x55ce0579fd40 <col:21, col:26> col:27 'FILE *'
|-FunctionDecl 0x55ce057a05c0 <line:859:1, col:35> col:12 __overflow 'int (FILE *, int)' extern
| |-ParmVarDecl 0x55ce057a0428 <col:24, col:29> col:30 'FILE *'
| `-ParmVarDecl 0x55ce057a04a8 <col:32> col:35 'int'
-FunctionDecl 0x5639c11966c0 <test.c:3:1, line:8:1> line:3:5 main 'int ()'
  `-CompoundStmt 0x5639c1196ac0 <col:11, line:8:1>
    |-DeclStmt 0x5639c1196800 <line:4:2, col:11>
    | `-VarDecl 0x5639c1196778 <col:2, col:10> col:6 used a 'int' cinit
    |   `-IntegerLiteral 0x5639c11967e0 <col:10> 'int' 1
    |-CallExpr 0x5639c1196910 <line:5:2, col:15> 'int'
    | |-ImplicitCastExpr 0x5639c11968f8 <col:2> 'int (*)(const char *, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x5639c1196818 <col:2> 'int (const char *, ...)' Function 0x5639c1186370 'printf' 'int (const char *, ...)'
    | |-ImplicitCastExpr 0x5639c1196958 <col:9> 'const char *' <NoOp>
    | | `-ImplicitCastExpr 0x5639c1196940 <col:9> 'char *' <ArrayToPointerDecay>
    | |   `-StringLiteral 0x5639c1196878 <col:9> 'char [3]' lvalue "%d"
    | `-ImplicitCastExpr 0x5639c1196970 <col:14> 'int' <LValueToRValue>
    |   `-DeclRefExpr 0x5639c1196898 <col:14> 'int' lvalue Var 0x5639c1196778 'a' 'int'
    |-CallExpr 0x5639c1196a38 <line:6:2, col:17> 'int'
    | |-ImplicitCastExpr 0x5639c1196a20 <col:2> 'int (*)(const char *, ...)' <FunctionToPointerDecay>
    | | `-DeclRefExpr 0x5639c1196988 <col:2> 'int (const char *, ...)' Function 0x5639c1186370 'printf' 'int (const char *, ...)'
    | `-ImplicitCastExpr 0x5639c1196a78 <col:9> 'const char *' <NoOp>
    |   `-ImplicitCastExpr 0x5639c1196a60 <col:9> 'char *' <ArrayToPointerDecay>
    |     `-StringLiteral 0x5639c11969e8 <col:9> 'char [7]' lvalue "test.."
    `-ReturnStmt 0x5639c1196ab0 <line:7:2, col:9>
      `-IntegerLiteral 0x5639c1196a90 <col:9> 'int' 0
```

#### CodeGen - IR(Intermediate Representation)中间代码生成

CodeGen 负责将语法树从顶至下遍历，翻译成 LLVM IR。

**LLVM IR 是 Frontend 的输出，LLVM Backend 的输入，前后端的桥接语言 **（Swift也是转成这个）

与 Objective-C Runtime 桥接

+ Class/Meta Class/Protocol/Category 内存结构生成，并存放在指定 section 中（如 Class：_DATA, _objc_classrefs）
+ Method/lvar/Property 内存结构生成
+ 组成 `method_list/ivar_list/property_list` 并填入 Class
+ Non-Fragile ABI：为每个 Ivar 合成 OBJC_IVAR_$_ 偏移值常量
+ 存取 Ivar 的语句`（ivar = 123; int a = ivar;）`转写成 base + OBJC_IVAR$_ 的形式
+ 将语法树中的 `ObjcMessageExpr` 翻译成相应版本的 `objc_msgSend`，对 super 关键字的调用翻译成 `objc_msgSendSuper`
+ 根据修饰符 `strong/weak/copy/atomic` 合成 `@property` 自动实现的 `setter/getter`
+ 处理 `@synthesize`
+ 生成 `block_layout` 的数据结构
+ 变量的 `capture(__block/__weak)`
+ 生成` _block_invoke` 函数
+ ARC：分析对象引用关系，将 `objc_storeStrong/objc_storeWeak` 等 ARC 代码插入
+ 将` ObjCAutoreleasePoolStmt `转译成 `objc_autoreleasePoolPush/Pop`
+ 实现自动调用 `[super dealloc]`
+ 为每个拥有 ivar 的 Class 合成` .cxx_destructor `方法来自动释放类的成员变量，代替 MRC 时代的`“self.xxx = nil”`


#### 一些例子

```
# 打印出未优化的llvm代码
clang-10 hello.c -S -emit-llvm -o -
# 设置优化级别为O3
clang-10 hello.c -S -emit-llvm -o - -O3
# 输出本机对应的机器码
clang-10 hello.c -S -O3 -o -
```

### 基于clang写解释器过程笔记

在写作业过程中，调试一般有两种方法，一种是使用gdb调试，一种是打印log以及利用打印ast树的方法明确每一个节点解析应该使用的类型以及方法：` clang -c -emit-llvm -fmodules -Xclang -ast-dump test.c`

关于使用gdb进行调试，这里进行简单介绍：

首先我们需要在`CMakeLists.txt`添加以下三行代码，提供调试符号信息等功能

```
set(CMAKE_BUILD_TYPE "Debug") 
set(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -g2 -ggdb") 
set(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS}") 
```

每次编写完代码需要make一下

```
cmake -DLLVM_DIR=/usr/local/llvm10ra/
make 
```

#### 解释预备阶段

在编写基于Clang的工具（例如Clang插件）或基于LibTooling的独立工具时，常见的入口点是FrontendAction。FrontendAction是一个界面，允许在编译过程中执行用户特定的操作。为了在AST上运行工具，提供了方便的接口ASTFrontendAction，该接口负责执行操作。剩下的唯一部分是实现CreateASTConsumer方法，该方法为每个translation unit返回ASTConsumer，其实也就是说在解析之前会先返回一个AST语法树，再去优先遍历每一个节点进行依次解释得到最后的结果。


```cpp
class InterpreterConsumer : public ASTConsumer {
public:
   explicit InterpreterConsumer(const ASTContext& context) : mEnv(),
   	   mVisitor(context, &mEnv) {
   }
   virtual ~InterpreterConsumer() {}

   virtual void HandleTranslationUnit(clang::ASTContext &Context) {
	   TranslationUnitDecl * decl = Context.getTranslationUnitDecl();
	   mEnv.init(decl);

	   FunctionDecl * entry = mEnv.getEntry();
	   mVisitor.VisitStmt(entry->getBody());
   }
private:
   Environment mEnv;
   InterpreterVisitor mVisitor;
};

class InterpreterClassAction : public ASTFrontendAction {
public: 
   virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
      clang::CompilerInstance &Compiler, llvm::StringRef InFile) {
      return std::unique_ptr<clang::ASTConsumer>(
         new InterpreterConsumer(Compiler.getASTContext()));
   }
};

int main (int argc, char ** argv) {
   if (argc > 1) {
      clang::tooling::runToolOnCode(std::unique_ptr<clang::FrontendAction>(new InterpreterClassAction), argv[1]);
   }
}
```

该解释器是基于LibTooling的，入口点是FrontendAction。FrontendAction是一个接口，它允许用户指定的actions作为编译的一部分来执行。为了在 `AST clang `上运行工具，AST clang 提供了方便的接口ASTFrontendAction，它负责执行action。剩下的唯一部分是实现CreateASTConsumer方法，该方法为每个翻译单元返回一个ASTConsumer。

`ASTConsumer`是一个用于在一个 AST 上编写通用`actions`的接口，而不管 AST 是如何生成的。`ASTConsumer`提供了许多不同的入口点，但是对于我们的用例来说，唯一需要的入口点是`HandleTranslationUnit`，它是用`ASTContext`为翻译单元调用的。使用`InterpreterConsumer(Compiler.getASTContext())`可以获取语法树，这里会先使用`mEnv.init(decl);`先扫描一次源码，把全局变量的定义以及函数的定义做一次声明，然后再根据语法树去遍历每一个节点来进行解释vistor即可；详细可以看这个[网站](https://blog.csdn.net/qq_23599965/article/details/90696621);

```
//若在全局上定义以下两个语句
//int a = 10;
//int b = a;

//解释以上两个语句打印的部分log：
		global var decl: 0x564414c09d58
		IntegerLiteral expr
		global var decl: 0x564414c09df8
		declref : a
		[*] bindStmt : DeclRefExpr 0x564414c09e60 10
		[*] getstmtval : DeclRefExpr 0x564414c09e60

```
init函数会先遍历一遍AST树获取所有声明
#### 解析AST树

参考：	[Clang Tutorial-CS453 Automated Software Testing](http://swtv.kaist.ac.kr/courses/cs453-fall14/lec5-Clang-tutorial.pdf)

在 Clang 中，可以理解有三种主要的类型，一个是decl声明(比如说FunctionDecl、VarDecl、VarDecl.etc)一个是语句（DeclStmt、WhileStmt、IfStmt. etc）还有一个是操作符号(binop)，下图是源码的的一个例子图：


  ![Alt text](/images/posts/clang/1602640842973.png)   
  

其中decl和stmt都有两个数据结构来bin每个节点以及其值：mVars和mExprs，他们都是使用C++ map映照容器存储的；map映照容器的元素数据是一个键值和一个映照数据组成的，键值与映照数据之间具有一一映照的关系。 map映照容器的数据结构是采用红黑树来实现的，插入键值的元素不允许重复，比较函数只对元素的键值进行比较，元素的各项数据可通过键值检索出来。插入元素，按键值的由小到大放入黑白树中。

![Alt text](/images/posts/clang/1603816314843.png)

上图源码对应的AST树为如下结构：

![Alt text](/images/posts/clang/1603816270371.png)

那么我们依据这个AST树去解释源码的时候，会从上到下遍历AST树节点，可以理解为在解释预备阶段创建了一个visitor，每当遇到一个节点都回开始去找改节点对应的visit函数，然后根据里面的visitstmt递归遍历解析树上的节点，在遇到操作符语句的时候会进行一定的操作（比如加减乘除）再bind到新的变量上进行赋值。

![Alt text](/images/posts/clang/1603817016762.png)

该图为解释上面源码的while前面部分代码的节点遍历顺序，这里会直接访问VisitDeclStmt，调用decl函数声明了变量a和b之后，继而返回后继续遍历AST body得到下一个节点BinaryOperator，因为VisitBinaryOperator中会继续先去遍历其子节点（其实是为了计算binop的左右节点才能进行相应的操作）；这里是先去访问DeclRefExpr节点，即调用VisitDeclRefExpr函数，因为该节点为AST树上的一个叶子节点，那么我们直接调用declref函数进行一些类型判断，然后获取该变量的原来的值再绑定到新的树节点上，执行完declref函数返回到VisitBinaryOperator函数下继续执行menv的binop(bop)函数。这就是上图中显示的整个流程，是一个简单的AST解释的顺序以及一些原则，后面将对各个节点类型的解释与处理进行详细的讲解。

#### 简单数据结构

mVars用于声明变量的值绑定;mExprs用于语句的值绑定等等

```
   	std::map<Decl*, int64_t> mVars;
   	std::map<Stmt*, int64_t> mExprs;
   	Stmt * mPC;
   	std::vector<StackFrame> mStack;
```
bindstmt：一元表达式绑定、callexpr、Expr、BinaryOperator.etc
bindDecl：VarDecl、DeclRefExpr、declexpr. etc
#### declstmt声明变量

VisitDeclStmt时会调用menv的decl函数，这个declstmt一般为叶子节点；主要用于声明变量，解析语句包括`int a; char a; int* a;int a[3];...`判断这些变量类型进行声明，解析的AST节点一般为如下结构。

![Alt text](/images/posts/clang/1603816030419.png)

实现源码：

```cpp
 // process DeclStmt,e.g. int a; int a=c+d; and etc.
virtual void VisitDeclStmt(DeclStmt * declstmt) {
	if(mEnv->haveReturn()){
		return;
     }  
	llvm::errs() << "[+] visit DeclStmt\n";
	mEnv->decl(declstmt);
}

	// 声明的变量，函数，枚举
   	void decl(DeclStmt * declstmt) {
		cout << "		[*] decl !!!" << endl;
	   	for (DeclStmt::decl_iterator it = declstmt->decl_begin(), ie = declstmt->decl_end(); it != ie; ++ it) {
			//in ast, the sub-node is usually VarDecl
			Decl * decl = *it;
			//VarDecl 表示变量声明或定义
		   	if (VarDecl * vardecl = dyn_cast<VarDecl>(decl)) {
				// global var
				// llvm::errs() << "decl: " << (vardecl->getType()).getAsString() << "\n";
				// llvm::errs() << "global var decl: " << vardecl << "\n";
				if (vardecl->getType().getTypePtr()->isIntegerType() || vardecl->getType().getTypePtr()->isPointerType() 
					|| vardecl->getType().getTypePtr()->isCharType() )
				{
					int val = 0;
					if (vardecl->hasInit()) {
						val = Expr_GetVal(vardecl->getInit());
					}
					mStack.back().bindDecl(vardecl, val);
				}else{
					//array
					if (auto array = dyn_cast<ConstantArrayType>(vardecl->getType().getTypePtr())){ 
					// array declstmt, bind a's addr to the vardecl.
						int64_t len = array->getSize().getLimitedValue();
						if (array->getElementType().getTypePtr()->isIntegerType()){ 
						// int a[3]; 
							int *a = new int[len];
							for (int i = 0; i < len; i++)
							{
								a[i] = 0x61;
							}
							// cout<<"[-] array init = "<<a<<endl;
							mStack.back().bindDecl(vardecl, (int64_t)a);
						}else if (array->getElementType().getTypePtr()->isCharType()){
						// char a[3];
							char *a = new char[len];
							for (int i = 0; i < len; i++)
							{
								a[i] = 0;
							}
							mStack.back().bindDecl(vardecl, (int64_t)a);
						}else if(array->getElementType().getTypePtr()->isPointerType()){ 
						// int* a[3];
							int64_t **a = new int64_t *[len];
							for (int i = 0; i < len; i++){
								a[i] = 0;
							}
							mStack.back().bindDecl(vardecl, (int64_t)a);
						}
					}
				}
		   	}
	   	}
   	}
```

#### DeclRefExpr引用已声明变量

VisitDeclRefExpr函数会在继续遍历其叶子节点后返回，调用env中的declref函数，这个函数会引用已声明的变量，比如int、char和pointer类型的。

```cpp

   // process DeclRefExpr, e.g. refered decl expr
   virtual void VisitDeclRefExpr(DeclRefExpr * expr) {
      if(mEnv->haveReturn()){
         return;
      }  
      llvm::errs() << "[+] visit DeclRefExpr\n";
	   VisitStmt(expr);
      // llvm::errs() << "[+] visitStmt VisitDeclRefExpr done\n";
	   mEnv->declref(expr);
   }

   	void declref(DeclRefExpr * declref) {
		llvm::errs() << "		declref : " << declref->getFoundDecl()->getNameAsString() << "\n";
	   	mStack.back().setPC(declref);
		if (declref->getType()->isCharType()){
			Decl *decl = declref->getFoundDecl();
			int64_t val = mStack.back().getDeclVal(decl);
			mStack.back().bindStmt(declref, val);
		}else if (declref->getType()->isIntegerType()) {
		   	Decl* decl = declref->getFoundDecl();
		   	int64_t val = mStack.back().getDeclVal(decl);
		   	mStack.back().bindStmt(declref, val);
	   	}else if (declref->getType()->isPointerType()){
			Decl *decl = declref->getFoundDecl();
			int64_t val = mStack.back().getDeclVal(decl);
			mStack.back().bindStmt(declref, val);
	   	} 
   	}
```

#### BinaryOperator 二元操作符

VisitBinaryOperator函数主要用来处理`=/+/-/*/>/</==/......`这些二元操作符，先判断该节点是否为赋值语句，会对子节点进行处理后进行赋值绑定，其他操作符同理。


#### IfStmt 条件语句

IfStmt、whilestmt、VisitForStmt的实现均基本同理，根据其语句的特点，特定位置判断类型后进行解释

```cpp
   //process ForStmt
   //https://clang.llvm.org/doxygen/Stmt_8h_source.html#l2451
   virtual void VisitForStmt(ForStmt *forstmt){
      // llvm::errs() << "[+] visit VisitForStmt\n";
      if(mEnv->haveReturn()){
         return;
      }  
      llvm::errs() << "[+] visit forstmt\n";
      if(Stmt *init = forstmt->getInit()){
         Visit(init);
      }
      for(; mEnv->Expr_GetVal(forstmt->getCond()); Visit(forstmt->getInc())){ //getCond 返回值是bool，而不是void，不能使用Visit，只能直接利用expr对该语句进行解析from ‘void’ to ‘bool’
         Stmt *body=forstmt->getBody();
         if(body && isa<CompoundStmt>(body)){
            Visit(forstmt->getBody());
         }
            
      }
   }
```

#### call and return

对于已定义不需要解析的库函数调用，比如：malloc、free、print等等这些函数，而其他自定义函数需要解析子函数得到返回结果的应该如何去解释处理呢？举个例子

```
extern int GET();
extern int * MALLOC(int);
extern void FREE(void *);
extern void PRINT(int);

int a = 10;

int f(int a){
	return a+10;
}

int main() {
	int b=1;
    int c=10;
	int a=b+c;
	a = f(a);
	PRINT(a);

}
```

这里调用了f这个自定义函数，上面源码的AST树是这样的：

![Alt text](/images/posts/clang/1603853199610.png)

![Alt text](/images/posts/clang/1603853362494.png)


解析AST树的过程中，解析到第一个CallExpr节点，也就是调用自定义函数f的时候，观察打印的log和AST树的结构可以对解析节点的顺序一目了然；这里需要注意的地方是调用子函数的时候需要push一个新的栈进行绑定变量，这里解析结束binop返回结果的时候也需要注意set一个return的标志位并绑定返回值（return之后需要把return标志位恢复）。

#### Expr_GetVal

这个是定义了一个函数接口用来获取节点上各种变量类型的值，或者遍历解析子节点获取语句的值。


#### 下一个大作业---基于llvm的函数调用解析

第一次大作业详细见[GitHub源码](https://github.com/ZoEplA/ast-interpreter )

下一个大作业:熟悉LLVM中间表示，use-def链, 对bitcode文件中的函数调用指令；判断函数直接调用与函数指针调用，计算出可能调用的函数并打印调用行号。