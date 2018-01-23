---
title: '1. Kaleidoscope: Tutorial Introduction and the Lexer'
date: 2018-01-10 15:42:44
tags: LLVM Tutorial
---

## 1.1 Tutorial Introduction

欢迎来到“[用LLVM实现一门语言](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)”教程。本教程完整展示了实现一门简单高级语言的过程，展现了LLVM的fun和easy。这个教程会帮你开始使用LLVM，并构建一个语言的框架，以后可以扩展到其他语言。教程里的代码也可以作为a playground to hack on other LLVM specific things.

<!-- more -->

<!-- comment 原文：
Welcome to the “Implementing a language with LLVM” tutorial. This tutorial runs through the implementation of a simple language, showing how fun and easy it can be. This tutorial will get you up and started as well as help to build a framework you can extend to other languages. The code in this tutorial can also be used as a playground to hack on other LLVM specific things.
-->

这篇教程的目标是逐渐展现这个高级语言的全貌，描述它从头构建的过程。这导致我们会广泛涉及到语言设计和LLVM特定用法的问题，我们会随着代码的进度逐渐展示和解释这些问题，不会一下子将你淹没在大量的细节问题中。

<!-- comment 原文：
The goal of this tutorial is to progressively unveil our language, describing how it is built up over time. This will let us cover a fairly broad range of language design and LLVM-specific usage issues, showing and explaining the code for it all along the way, without overwhelming you with tons of details up front.
-->

需要指出的是，我们的教程只涉及编译技术和LLVM，不包括现代软件工程设计原则。实际上，我们会用一些违反软件设计原则的代码来简化知识的阐述过程，比如说，代码会使用全局变量，而不是使用精心的软件设计。如果你深入研究，并且将这些代码用作未来project的基础，解决这些问题不会太难。

<!-- comment 原文：
It is useful to point out ahead of time that this tutorial is really about teaching compiler techniques and LLVM specifically, not about teaching modern and sane software engineering principles. In practice, this means that we’ll take a number of shortcuts to simplify the exposition. For example, the code uses global variables all over the place, doesn’t use nice design patterns like [visitors](http://en.wikipedia.org/wiki/Visitor_pattern), etc... but it is very simple. If you dig in and use the code as a basis for future projects, fixing these deficiencies shouldn’t be hard.
-->

我将教程按章节整理起来，以便读者根据需要阅读某些章节，教程的结构如下：

<!-- comment 原文：
I’ve tried to put this tutorial together in a way that makes chapters easy to skip over if you are already familiar with or are uninterested in the various pieces. The structure of the tutorial is:
-->

* Chapter #1：`Kaleidoscope`语言简介，以及它的词法分析器(Lexer)的定义。这一节展示了我们要做什么，以及我们希望完成的基本功能。为了让这篇教程的可读性和hackable最大化，我们不会用词法和语法的生成器，而是用C++实现所有东西。但是LLVM和这些生成器可以很好的一起工作，如果你更喜欢用这些工具的话完全ok。

<!-- comment 原文：
* Chapter #1: Introduction to the Kaleidoscope language, and the definition of its Lexer - This shows where we are going and the basic functionality that we want it to do. In order to make this tutorial maximally understandable and hackable, we choose to implement everything in C++ instead of using lexer and parser generators. LLVM obviously works just fine with such tools, feel free to use one if you prefer.
  -->

* Chapter #2：实现语法分析和抽象语法树(AST)。词法分析器完成后，我们可以讨论语法分析技术和基本的AST构造。这篇教程使用了递归下降分析法和算符有限分析法。Chapter  1和2中的东西都不是针对LLVM的，此时代码还和LLVM没有多少关系。

<!-- comment 原文：
* Chapter #2: Implementing a Parser and AST - With the lexer in place, we can talk about parsing techniques and basic AST construction. This tutorial describes recursive descent parsing and operator precedence parsing. Nothing in Chapters 1 or 2 is LLVM-specific, the code doesn’t even link in LLVM at this point. :) 
  -->

* Chapter #3：生成LLVM IR。
* Chapter #3: Code generation to LLVM IR - With the AST ready, we can show off how easy generation of LLVM IR really is.

* Chapter #4: Adding JIT and Optimizer Support - Because a lot of people are interested in using LLVM as a JIT, we’ll dive right into it and show you the 3 lines it takes to add JIT support. LLVM is also useful in many other ways, but this is one simple and “sexy” way to show off its power. :)

* Chapter #5: Extending the Language: Control Flow - With the language up and running, we show how to extend it with control flow operations (if/then/else and a ‘for’ loop). This gives us a chance to talk about simple SSA construction and control flow.

* Chapter #6: Extending the Language: User-defined Operators - This is a silly but fun chapter that talks about extending the language to let the user program define their own arbitrary unary and binary operators (with assignable precedence!). This lets us build a significant piece of the “language” as library routines.

* Chapter #7: Extending the Language: Mutable Variables - This chapter talks about adding user-defined local variables along with an assignment operator. The interesting part about this is how easy and trivial it is to construct SSA form in LLVM: no, LLVM does not require your front-end to construct SSA form!

* Chapter #8: Compiling to Object Files - This chapter explains how to take LLVM IR and compile it down to object files.

* Chapter #9: Extending the Language: Debug Information - Having built a decent little programming language with control flow, functions and mutable variables, we consider what it takes to add debug information to standalone executables. This debug information will allow you to set breakpoints in Kaleidoscope functions, print out argument variables, and call functions - all from within the debugger!

* Chapter #10: Conclusion and other useful LLVM tidbits - This chapter wraps up the series by talking about potential ways to extend the language, but also includes a bunch of pointers to info about “special topics” like adding garbage collection support, exceptions, debugging, support for “spaghetti stacks”, and a bunch of other tips and tricks.

By the end of the tutorial, we’ll have written a bit less than 1000 lines of non-comment, non-blank, lines of code. With this small amount of code, we’ll have built up a very reasonable compiler for a non-trivial language including a hand-written lexer, parser, AST, as well as code generation support with a JIT compiler. While other systems may have interesting “hello world” tutorials, I think the breadth of this tutorial is a great testament to the strengths of LLVM and why you should consider it if you’re interested in language or compiler design.

A note about this tutorial: we expect you to extend the language and play with it on your own. Take the code and go crazy hacking away at it, compilers don’t need to be scary creatures - it can be a lot of fun to play with languages!

## 1.2 The Basic Language

这篇教程将会以我们称为"[Kaleidoscope](http://en.wikipedia.org/wiki/Kaleidoscope)"的toy language作为例子。Kaleidoscope作为一门编程语言，允许定义functions，使用条件语言，数学公式等。通过完整的教程，我们将扩展Kaleidoscope，让它支持if/then/else结构、for循环、用户定义的运算符、有一个简单命令交互的JIT编译器，等等。

<!-- comment
This tutorial will be illustrated with a toy language that we’ll call "[Kaleidoscope](http://en.wikipedia.org/wiki/Kaleidoscope)" (derived from “meaning beautiful, form, and view”). Kaleidoscope is a procedural language that allows you to define functions, use conditionals, math, etc. Over the course of the tutorial, we’ll extend Kaleidoscope to support the if/then/else construct, a for loop, user defined operators, JIT compilation with a simple command line interface, etc.
-->

简单起见，Kaleidoscope中唯一的数据类型是64位浮点数（同C语言中的`double`）。这样一来，程序中所有的值都是双精度的浮点数，程序中的变量不需要声明变量类型。这样一来，Kaleidoscope语言的语法就比较优雅和简单了，举例来说，下面这个简单的程序可以计算[Fibonacci数列](http://en.wikipedia.org/wiki/Fibonacci_number)：

<!-- comment
Because we want to keep things simple, the only datatype in Kaleidoscope is a 64-bit floating point type (aka ‘double’ in C parlance). As such, all values are implicitly double precision and the language doesn’t require type declarations. This gives the language a very nice and simple syntax. For example, the following simple example computes [Fibonacci numbers](http://en.wikipedia.org/wiki/Fibonacci_number):
-->

```
# Compute the x'th fibonacci number.
def fib(x)
  if x < 3 then
    1
  else
    fib(x-1)+fib(x-2)

# This expression will compute the 40th number.
fib(40)
```

Kaleidoscope可以调用标准库中的函数（LLVM JIT让实现这个特性变得颇为简单）。这意味着你可以使用'`extern`'关键字，在你使用之前去定义函数（这一点对mutually recursive functions也很有用）。举个例子:

<!--comment
We also allow Kaleidoscope to call into standard library functions (the LLVM JIT makes this completely trivial). This means that you can use the ‘extern’ keyword to define a function before you use it (this is also useful for mutually recursive functions). For example:
-->

```
extern sin(arg);
extern cos(arg);
extern atan2(arg1 arg2);

atan2(sin(.4), cos(42))
```

在第6章有一个更有趣的例子——我们用Kaleidoscope写了一个[displays a Mandelbrot Set](http://llvm.org/docs/tutorial/LangImpl06.html#kicking-the-tires) at various levels of magnification的小程序。

<!-- comment
A more interesting example is included in Chapter 6 where we write a little Kaleidoscope application that [displays a Mandelbrot Set](http://llvm.org/docs/tutorial/LangImpl06.html#kicking-the-tires) at various levels of magnification.
-->

下面，让我们开始实现这门程序语言吧！

<!-- comment
Lets dive into the implementation of this language!
-->

## 1.3. The Lexer

实现一门程序语言的首要任务是处理文本文件，识别代码的内容。做这件事的传统方法是使用[lexer](http://en.wikipedia.org/wiki/Lexical_analysis)（也称为"scanner"），来将输入分割成"tokens"。每个token包含了一个token码，可能还包含一些metadata（比如数字的数值）。首先，我们定义所有可能的token：

* （译者注）metadata : Information that describes other information in order to help you understand or use it.

<!-- comment
When it comes to implementing a language, the first thing needed is the ability to process a text file and recognize what it says. The traditional way to do this is to use a “[lexer](http://en.wikipedia.org/wiki/Lexical_analysis)” (aka ‘scanner’) to break the input up into “tokens”. Each token returned by the lexer includes a token code and potentially some metadata (e.g. the numeric value of a number). First, we define the possibilities:
-->

```C++
// The lexer returns tokens [0-255] if it is an unknown character, otherwise one
// of these for known things.
enum Token {
  tok_eof = -1,

  // commands
  tok_def = -2,
  tok_extern = -3,

  // primary
  tok_identifier = -4,
  tok_number = -5,
};

static std::string IdentifierStr; // Filled in if tok_identifier
static double NumVal;             // Filled in if tok_number
```

lexer返回的每个token，要么是Token枚举值中的一个，要么是一个“未知的”字符比如‘+’（返回的是它的ASCII值）。如果正在处理的token是一个标识符，全局变量`IdentifierStr`会保存这个标识符的名字。如果正在处理的token是一个数值量（比如1.0），`NumVal`会保存它的值。需要注意的是，简单起见，我们在这里使用全局变量，而在真正的程序语言实现中，这不是一个好的选择。

<!-- comment
Each token returned by our lexer will either be one of the Token enum values or it will be an ‘unknown’ character like ‘+’, which is returned as its ASCII value. If the current token is an identifier, the `IdentifierStr` global variable holds the name of the identifier. If the current token is a numeric literal (like 1.0), `NumVal` holds its value. Note that we use global variables for simplicity, this is not the best choice for a real language implementation :).
-->

lexer的实现是一个名为`gettok`的函数，这个函数读入standard input，并返回下一个token。函数的开头部分如下：

<!-- comment
The actual implementation of the lexer is a single function named `gettok`. The `gettok` function is called to return the next token from standard input. Its definition starts as:
-->

```C++
/// gettok - Return the next token from standard input.
static int gettok() {
  static int LastChar = ' ';

  // Skip any whitespace.
  while (isspace(LastChar))
    LastChar = getchar();
```

`gettok`不断调用C语言的`getchar()`函数，每次从standard input读取一个字符。`gettok`读入并识别，并将最后一个字符保存在`LastChar`中，但是并不做任何处理。`gettok`要做的第一件事情就是忽略tokens之间所有的空格，这一点是通过上面代码中的循环来实现的。

<!-- comment
`gettok` works by calling the C `getchar()` function to read characters one at a time from standard input. It eats them as it recognizes them and stores the last character read, but not processed, in LastChar. The first thing that it has to do is ignore whitespace between tokens. This is accomplished with the loop above.
-->

`gettok`需要做的下一件事是识别标识符和特殊的关键字（比如“def”）。Kaleidoscope通过一个简单的循环来做到这一点：

<!-- comment
The next thing `gettok` needs to do is recognize identifiers and specific keywords like “def”. Kaleidoscope does this with this simple loop:
-->

```C++
if (isalpha(LastChar)) { // identifier: [a-zA-Z][a-zA-Z0-9]*
  IdentifierStr = LastChar;
  while (isalnum((LastChar = getchar())))
    IdentifierStr += LastChar;

  if (IdentifierStr == "def")
    return tok_def;
  if (IdentifierStr == "extern")
    return tok_extern;
  return tok_identifier;
}
```

这段代码在识别出一个标识符后，会设置全局变量`IdentifierStr`的值。同样的，程序语言的关键字会在同一个循环里被识别出来。数字的识别和标识符的识别类似：

<!-- comment
Note that this code sets the ‘`IdentifierStr`‘ global whenever it lexes an identifier. Also, since language keywords are matched by the same loop, we handle them here inline. Numeric values are similar:
-->

```C++
if (isdigit(LastChar) || LastChar == '.') {   // Number: [0-9.]+
  std::string NumStr;
  do {
    NumStr += LastChar;
    LastChar = getchar();
  } while (isdigit(LastChar) || LastChar == '.');

  NumVal = strtod(NumStr.c_str(), 0);
  return tok_number;
}
```

这是一段非常直观的代码。当从input中读取到数值常量时，我们用C语言的`strtod`函数来将存储在`NumStr`中的字符串转换为数值，并存储在`NumVal`中。需要注意的是，这里并没有做足够的错误检查：这段代码可以错误地读入“1.23.45.67“这样的输入，并将它处理为你输入的是”1.23“。暂时可以不用管它，feel free :)。接下来我们处理注释：

<!--
This is all pretty straight-forward code for processing input. When reading a numeric value from input, we use the C `strtod` function to convert it to a numeric value that we store in `NumVal`. Note that this isn’t doing sufficient error checking: it will incorrectly read “1.23.45.67” and handle it as if you typed in “1.23”. Feel free to extend it :). Next we handle comments:
-->

```C++
if (LastChar == '#') {
  // Comment until end of line.
  do
    LastChar = getchar();
  while (LastChar != EOF && LastChar != '\n' && LastChar != '\r');

  if (LastChar != EOF)
    return gettok();
}
```

我们处理注释的方法是，忽略本行所有字符后，如果读到EOF就结束词法分析，否则返回下一个token。最后，如果输入不符合上面任何一个case的话，那么它要么是一个操作符（比如‘+’），要么是文件结尾。通过下面这段代码处理：

<!--
We handle comments by skipping to the end of the line and then return the next token. Finally, if the input doesn’t match one of the above cases, it is either an operator character like ‘+’ or the end of the file. These are handled with this code:
-->

```C++
  // Check for end of file.  Don't eat the EOF.
  if (LastChar == EOF)
    return tok_eof;

  // Otherwise, just return the character as its ascii value.
  int ThisChar = LastChar;
  LastChar = getchar();
  return ThisChar;
}
```

这样一来，我们就基本完成了Kaleidoscope语言的lexer（Lexer的[完整代码列表](http://llvm.org/docs/tutorial/LangImpl02.html#full-code-listing)在[下一节](http://llvm.org/docs/tutorial/LangImpl02.html)）。接下来，我们将[构造一个简单的语法分析器](http://llvm.org/docs/tutorial/LangImpl02.html)，然后构造一个抽象语法树。完成这些之后，我们会引入一个driver，可以将词法分析器和语法分析器一起使用。

<!--
With this, we have the complete lexer for the basic Kaleidoscope language (the [full code listing](http://llvm.org/docs/tutorial/LangImpl02.html#full-code-listing) for the Lexer is available in the [next chapter](http://llvm.org/docs/tutorial/LangImpl02.html) of the tutorial). Next we’ll [build a simple parser that uses this to build an Abstract Syntax Tree](http://llvm.org/docs/tutorial/LangImpl02.html). When we have that, we’ll include a driver so that you can use the lexer and parser together.
-->