---
title: '4. Kaleidoscope: Adding JIT and Optimizer Support'
date: 2018-01-11 21:25:57
tags: LLVM Tutorial
---

## 4.1. Chapter 4 Introduction

欢迎来到“[用LLVM实现一门编程语言](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)”教程第4章。第1-3章描述了一个简单的编程语言的实现，并添加了生成LLVM IR的支持。这一章将会描述两个新技术：为你的语言增加优化支持，以及增加即使编译支持。这两个新增的技术将会展示如何获得Kaleidoscope语言的优雅、高效的代码。

<!-- more -->

<!-- Welcome to Chapter 4 of the “[Implementing a language with LLVM](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)” tutorial. Chapters 1-3 described the implementation of a simple language and added support for generating LLVM IR. This chapter describes two new techniques: adding optimizer support to your language, and adding JIT compiler support. These additions will demonstrate how to get nice, efficient code for the Kaleidoscope language. -->

## 4.2. Trivial Constant Folding

我们在第3章中的示范非常优雅，而且容易扩展。但是，它并没有生成完美的代码。IRBuild在编译这段简单的代码中只进行了最基本的优化。

<!-- Our demonstration for Chapter 3 is elegant and easy to extend. Unfortunately, it does not produce wonderful code. The IRBuilder, however, does give us obvious optimizations when compiling simple code: -->

```bash
ready> def test(x) 1+2+x;
Read function definition:
define double @test(double %x) {
entry:
        %addtmp = fadd double 3.000000e+00, %x
        ret double %addtmp
}
```

上面的代码并不是对AST的直接翻译。对输入进行语法分析后生成的AST的直接翻译应该是下面这样：

<!-- This code is not a literal transcription of the AST built by parsing the input. That would be: -->

```bash
ready> def test(x) 1+2+x;
Read function definition:
define double @test(double %x) {
entry:
        %addtmp = fadd double 2.000000e+00, 1.000000e+00
        %addtmp1 = fadd double %addtmp, %x
        ret double %addtmp1
}
```

常量折叠（Constant folding），正如上面所见，是一种非常常见且重要的优化：很多编程语言的实现里都在它们的AST表示中包含了常量折叠的支持。

<!-- Constant folding, as seen above, in particular, is a very common and very important optimization: so much so that many language implementors implement constant folding support in their AST representation. -->

使用LLVM，你不需要在AST中增加这项支持。因为所有创建LLVM IR的调用都会经过LLVM IR builder，在你调用时，builder会检查是否有常量折叠的机会，如果有，它就会进行常量折叠，并且返回一个constant而不是创建一条instruction。

<!-- With LLVM, you don’t need this support in the AST. Since all calls to build LLVM IR go through the LLVM IR builder, the builder itself checked to see if there was a constant folding opportunity when you call it. If so, it just does the constant fold and return the constant instead of creating an instruction. -->

实际中，我们推荐在生成代码时，总应该使用`IRBuilder`。它没有“syntactic overhead”（你不需要在每个地方增加常量折叠检查，让你的编译器代码变得复杂），而且在某些情况下，它可以减少生成的LLVM IR的代码总量（尤其是对于有宏预处理或者使用大量constants的编程语言）。

<!-- Well, that was easy :). In practice, we recommend always using `IRBuilder` when generating code like this. It has no “syntactic overhead” for its use (you don’t have to uglify your compiler with constant checks everywhere) and it can dramatically reduce the amount of LLVM IR that is generated in some cases (particular for languages with a macro preprocessor or that use a lot of constants). -->

另一方面，`IRBuilder`的能力也有局限，它只在它要构造的代码内部做分析和优化。如果你用一个稍微复杂一点的例子：

<!-- On the other hand, the `IRBuilder` is limited by the fact that it does all of its analysis inline with the code as it is built. If you take a slightly more complex example: -->

```bash
ready> def test(x) (1+2+x)*(x+(1+2));
ready> Read function definition:
define double @test(double %x) {
entry:
        %addtmp = fadd double 3.000000e+00, %x
        %addtmp1 = fadd double %x, 3.000000e+00
        %multmp = fmul double %addtmp, %addtmp1
        ret double %multmp
}
```

在上面的情况中，乘法的LHS和RHS是相同的值。我们希望可以生成“`tmp = x+3; result = tmp*tmp;`”，而不是两次计算“`x+3`”。

<!-- In this case, the LHS and RHS of the multiplication are the same value. We’d really like to see this generate “`tmp = x+3; result = tmp*tmp;`” instead of computing “`x+3`” twice. -->

不幸的是，没有哪个局部分析可以检测并优化这种情况。这种优化需要两次转换：表达式的重组（让加法在词法分析层面完全相同），以及消除公共子表达式（CSE）来检测冗余的加法指令。幸运的是，LLVM提供了大量的优化，以“passes”的形式。

<!-- Unfortunately, no amount of local analysis will be able to detect and correct this. This requires two transformations: reassociation of expressions (to make the add’s lexically identical) and Common Subexpression Elimination (CSE) to delete the redundant add instruction. Fortunately, LLVM provides a broad range of optimizations that you can use, in the form of “passes”. -->

## 4.3. LLVM Optimization Passes

LLVM提供了很多优化passes，可以做很多种事情，提供多种tradeoffs。和其他的系统不同，LLVM摒弃了一套优化可以处理所有语言和所有情况的错误观念。LLVM允许编译器实现者完全决定做哪些优化，用什么顺序优化，以及在哪些情形下做优化。

<!--LLVM provides many optimization passes, which do many different sorts of things and have different tradeoffs. Unlike other systems, LLVM doesn’t hold to the mistaken notion that one set of optimizations is right for all languages and for all situations. LLVM allows a compiler implementor to make complete decisions about what optimizations to use, in which order, and in what situation.-->

LLVM支持“whole module” passes，也支持“per-function” passes。“whole module” passes会对全部代码尽可能的做分析（通常是一个完整的文件，但如果在link时做分析，可能只能分析完整程序的一部分）。“per-function” passes一次只对一个函数进行分析。更多关于pass以及pass如何运行的信息，参见[How to Write a Pass](https://releases.llvm.org/5.0.0/docs/WritingAnLLVMPass.html)文档，以及[List of LLVM Passes](https://releases.llvm.org/5.0.0/docs/Passes.html)。

<!-- As a concrete example, LLVM supports both “whole module” passes, which look across as large of body of code as they can (often a whole file, but if run at link time, this can be a substantial portion of the whole program). It also supports and includes “per-function” passes which just operate on a single function at a time, without looking at other functions. For more information on passes and how they are run, see the [How to Write a Pass](https://releases.llvm.org/5.0.0/docs/WritingAnLLVMPass.html) document and the [List of LLVM Passes](https://releases.llvm.org/5.0.0/docs/Passes.html). -->

对Kaleidoscope来说，我们现在是用户输入后，动态地生成函数，每次生成一个。这里我们并没有追求完美的优化体验，但我们也会在可能的情况下让事情简单快速。这样一来，我们将会选择运行一些per-function优化，在用户输入function之后。如果我们想制作一个“静态Kaleidoscope编译器”，我们将会使用我们现在已有的代码，但是我们会将优化步骤推迟到对全部文件进行语法分析完成之后。

<!-- For Kaleidoscope, we are currently generating functions on the fly, one at a time, as the user types them in. We aren’t shooting for the ultimate optimization experience in this setting, but we also want to catch the easy and quick stuff where possible. As such, we will choose to run a few per-function optimizations as the user types the function in. If we wanted to make a “static Kaleidoscope compiler”, we would use exactly the code we have now, except that we would defer running the optimizer until the entire file has been parsed. -->

为了执行per-function优化，我们需要安装[FunctionPassManager](https://releases.llvm.org/5.0.0/docs/WritingAnLLVMPass.html#what-passmanager-doesr)来管理我们想运行的LLVM优化器。当我们设置好后，就可以增加一系列的优化器。对每个想要优化的module，都需要增加一个新的FunctionPassManager，所以我们写了一个函数去创建并初始化module和pass manager：

<!-- In order to get per-function optimizations going, we need to set up a [FunctionPassManager](https://releases.llvm.org/5.0.0/docs/WritingAnLLVMPass.html#what-passmanager-doesr) to hold and organize the LLVM optimizations that we want to run. Once we have that, we can add a set of optimizations to run. We’ll need a new FunctionPassManager for each module that we want to optimize, so we’ll write a function to create and initialize both the module and pass manager for us: -->

```C++
void InitializeModuleAndPassManager(void) {
  // Open a new module.
  TheModule = llvm::make_unique<Module>("my cool jit", TheContext);

  // Create a new pass manager attached to it.
  TheFPM = llvm::make_unique<FunctionPassManager>(TheModule.get());

  // Do simple "peephole" optimizations and bit-twiddling optzns.
  TheFPM->add(createInstructionCombiningPass());
  // Reassociate expressions.
  TheFPM->add(createReassociatePass());
  // Eliminate Common SubExpressions.
  TheFPM->add(createGVNPass());
  // Simplify the control flow graph (deleting unreachable blocks, etc).
  TheFPM->add(createCFGSimplificationPass());

  TheFPM->doInitialization();
}
```

上面的代码初始化了一个全局的module `TheModule`，以及一个function pass manager `TheFPM`，并连接到`TheModule`。当pass manager设置好后，我们用了一系列的”add“调用来增加一系列的LLVM passes。

<!-- This code initializes the global module `TheModule`, and the function pass manager `TheFPM`, which is attached to `TheModule`. Once the pass manager is set up, we use a series of “add” calls to add a bunch of LLVM passes. -->

在这个情况下，我们选择添加四个优化passes。我们选择的passes是一组比较标准的”cleanup“优化，对很多代码都有用。我们不会深入探讨它们做了什么，但是相信我，它们是一个很好的起点。

<!-- In this case, we choose to add four optimization passes. The passes we choose here are a pretty standard set of “cleanup” optimizations that are useful for a wide variety of code. I won’t delve into what they do but, believe me, they are a good starting place :). -->

当PassManager设置好后，我们需要使用它。这一步运行在新创建的函数构造好（通过in `FunctionAST::codegen()`）之后，返回给用户之前。

<!-- Once the PassManager is set up, we need to make use of it. We do this by running it after our newly created function is constructed (in `FunctionAST::codegen()`), but before it is returned to the client: -->

```C++
if (Value *RetVal = Body->codegen()) {
  // Finish off the function.
  Builder.CreateRet(RetVal);

  // Validate the generated code, checking for consistency.
  verifyFunction(*TheFunction);

  // Optimize the function.
  TheFPM->run(*TheFunction);

  return TheFunction;
}
```

正如你所见，这一切都很直观。`FunctionPassManager`在合适的地方优化并更新了LLVM Fucntion\*，（可能）改进了函数体。这时，我们可以重新试验一下之前的代码：

<!-- As you can see, this is pretty straightforward. The `FunctionPassManager` optimizes and updates the LLVM Function\* in place, improving (hopefully) its body. With this in place, we can try our test above again: -->

```bash
ready> def test(x) (1+2+x)*(x+(1+2));
ready> Read function definition:
define double @test(double %x) {
entry:
        %addtmp = fadd double %x, 3.000000e+00
        %multmp = fmul double %addtmp, %addtmp
        ret double %multmp
}
```

正如所期望的样子，我们现在获得了优化后的代码，优化后这个函数每次执行时都可以节省一条浮点加法指令。

<!-- As expected, we now get our nicely optimized code, saving a floating point add instruction from every execution of this function. -->

LLVM提供了很多种类的优化，可以在不同的情境中使用。你可以参考一些[documentation about the various passes](https://releases.llvm.org/5.0.0/docs/Passes.html)，但它们并不很完整。另一个ideas的好来源是从看`Clang`运行哪些passes开始。“`opt`”工具允许你在命令行中试验passes，这样你就可以看出它们是否让代码做出某些改变。

<!-- LLVM provides a wide variety of optimizations that can be used in certain circumstances. Some [documentation about the various passes](https://releases.llvm.org/5.0.0/docs/Passes.html) is available, but it isn’t very complete. Another good source of ideas can come from looking at the passes that `Clang` runs to get started. The “`opt`” tool allows you to experiment with passes from the command line, so you can see if they do anything. -->

现在从我们的前端生成了不错的代码，让我们开始讨论如何运行他们！

<!-- Now that we have reasonable code coming out of our front-end, lets talk about executing it! -->

## 4.4. Adding a JIT Compiler

有很多种类的工具可以应用在LLVM IR上。比如说，你可以运行优化器（就像上面做的那样），可以dump out成文本或者二进制格式，可以编译成某些平台上的汇编文件（.s），也可以即时编译。LLVM IR的好处就在于它是一种编译器不同部分之间的“通用格式”。

<!-- Code that is available in LLVM IR can have a wide variety of tools applied to it. For example, you can run optimizations on it (as we did above), you can dump it out in textual or binary forms, you can compile the code to an assembly file (.s) for some target, or you can JIT compile it. The nice thing about the LLVM IR representation is that it is the “common currency” between many different parts of the compiler. -->

在这一节中，我们将为我们的解释器增加即时编译支持。基本思路是用户输入函数体时和当前一样，但是输入顶层表达式时，立即计算出表达式的值。比如说，如果用户输入“1+2”，我们应该计算并输出3。如果用户定义了一个函数，用户应该可以从命令行调用这个函数。

<!-- In this section, we’ll add JIT compiler support to our interpreter. The basic idea that we want for Kaleidoscope is to have the user enter function bodies as they do now, but immediately evaluate the top-level expressions they type in. For example, if they type in “1 + 2;”, we should evaluate and print out 3. If they define a function, they should be able to call it from the command line. -->

为此，我们首先需要为本机准备创建代码的环境，创建并初始化JIT。这一步可以通过调用一些`InitializeNativeTarget\*`函数，并添加一个全局变量`TheJIT`，然后在`main`中初始化：

<!-- In order to do this, we first prepare the environment to create code for the current native target and declare and initialize the JIT. This is done by calling some `InitializeNativeTarget\*` functions and adding a global variable `TheJIT`, and initializing it in `main`: -->

```C++
static std::unique_ptr<KaleidoscopeJIT> TheJIT;
...
int main() {
  InitializeNativeTarget();
  InitializeNativeTargetAsmPrinter();
  InitializeNativeTargetAsmParser();

  // Install standard binary operators.
  // 1 is lowest precedence.
  BinopPrecedence['<'] = 10;
  BinopPrecedence['+'] = 20;
  BinopPrecedence['-'] = 20;
  BinopPrecedence['*'] = 40; // highest.

  // Prime the first token.
  fprintf(stderr, "ready> ");
  getNextToken();

  TheJIT = llvm::make_unique<KaleidoscopeJIT>();

  // Run the main "interpreter loop" now.
  MainLoop();

  return 0;
}
```

我们还需要设置JIT的data layout：

<!-- We also need to setup the data layout for the JIT: -->

```C++
void InitializeModuleAndPassManager(void) {
  // Open a new module.
  TheModule = llvm::make_unique<Module>("my cool jit", TheContext);
  TheModule->setDataLayout(TheJIT->getTargetMachine().createDataLayout());

  // Create a new pass manager attached to it.
  TheFPM = llvm::make_unique<FunctionPassManager>(TheModule.get());
  ...
```

KaleidoscopeJIT类是为这些教程设计的一个简单的JIT，包含在LLVM源代码中，位于llvm-src/examples/Kaleidoscope/include/KaleidoscopeJIT.h。在后面的章节里我们将会展示它是如何工作的，并扩展出新特性，但是现在我们只是使用它。它的API非常简单：`addModule`为JIT增加一个LLVM IR module，让它的函数可以执行；`removeModule`移除一个module，释放那个module中的所有内存；`findSymbol`让我们可以找到编译后代码的pointers。

<!-- The KaleidoscopeJIT class is a simple JIT built specifically for these tutorials, available inside the LLVM source code at llvm-src/examples/Kaleidoscope/include/KaleidoscopeJIT.h. In later chapters we will look at how it works and extend it with new features, but for now we will take it as given. Its API is very simple: `addModule` adds an LLVM IR module to the JIT, making its functions available for execution; `removeModule` removes a module, freeing any memory associated with the code in that module; and `findSymbol` allows us to look up pointers to the compiled code. -->

我们可以使用这些简单的API，改变我们的代码，对顶层表达式进行语法分析如下：

<!-- We can take this simple API and change our code that parses top-level expressions to look like this:  --> 

```C++
static void HandleTopLevelExpression() {
  // Evaluate a top-level expression into an anonymous function.
  if (auto FnAST = ParseTopLevelExpr()) {
    if (FnAST->codegen()) {

      // JIT the module containing the anonymous expression, keeping a handle so
      // we can free it later.
      auto H = TheJIT->addModule(std::move(TheModule));
      InitializeModuleAndPassManager();

      // Search the JIT for the __anon_expr symbol.
      auto ExprSymbol = TheJIT->findSymbol("__anon_expr");
      assert(ExprSymbol && "Function not found");

      // Get the symbol's address and cast it to the right type (takes no
      // arguments, returns a double) so we can call it as a native function.
      double (*FP)() = (double (*)())(intptr_t)ExprSymbol.getAddress();
      fprintf(stderr, "Evaluated to %f\n", FP());

      // Delete the anonymous expression module from the JIT.
      TheJIT->removeModule(H);
    }
```

如果语法分析和codegen成功，下一步就是在JIT中添加包含顶层表达式的module。我们通过调用addModule来完成这件事，它会为这个module中所有函数进行代码生成，并且返回一个句柄，这个句柄将会在后面从JIT中删除module时用到。当module添加到JIT后，就不能再修改了，所以我们通过调用`InitializeModuleAndPassManager()`创建了一个新的module保存后面的代码。

<!-- If parsing and codegen succeeed, the next step is to add the module containing the top-level expression to the JIT. We do this by calling addModule, which triggers code generation for all the functions in the module, and returns a handle that can be used to remove the module from the JIT later. Once the module has been added to the JIT it can no longer be modified, so we also open a new module to hold subsequent code by calling `InitializeModuleAndPassManager()`. -->

当我们向JIT添加module后，我们需要获取指向最终生成的代码的指针。我们通过调用JIT的findSymbol方法来做这件事，并且传递顶层表达式函数的名字：`__anon_expr`。因为我们只添加了一个函数，我们在findSymbol返回结果后添加了一个assert。

<!-- Once we’ve added the module to the JIT we need to get a pointer to the final generated code. We do this by calling the JIT’s findSymbol method, and passing the name of the top-level expression function: `__anon_expr`. Since we just added this function, we assert that findSymbol returned a result. -->

下面，我们通过在symbol上调用`getAddress()`获得`__anon_expr`函数的内存地址。之前我们将顶层表达式编译成为一个LLVM函数，不接受任何参数，返回double型的表达式的计算结果。因为LLVM JIT编译器匹配了本地硬件平台应用程序二进制接口（ABI），这意味着你可以you can just cast the result pointer to a function pointer of that type and call it directly。这样一来，JIT编译得到的代码和静态链接到你的程序的本机代码就没有区别了。

<!-- Next, we get the in-memory address of the `__anon_expr` function by calling `getAddress()` on the symbol. Recall that we compile top-level expressions into a self-contained LLVM function that takes no arguments and returns the computed double. Because the LLVM JIT compiler matches the native platform ABI, this means that you can just cast the result pointer to a function pointer of that type and call it directly. This means, there is no difference between JIT compiled code and native machine code that is statically linked into your application. -->

最后，因为我们不支持顶层表达式的重新计算，在计算完后，我们会将module从JIT移除，并释放相关的内存。但是，要记得，我们在几行前创建的module（通过`InitializeModuleAndPassManager`建立的）仍然存在，并等待新代码。

<!-- Finally, since we don’t support re-evaluation of top-level expressions, we remove the module from the JIT when we’re done to free the associated memory. Recall, however, that the module we created a few lines earlier (via `InitializeModuleAndPassManager`) is still open and waiting for new code to be added. -->

添加了这两个改变后，让我们看看Kaleidoscope现在是怎样工作的！

<!-- With just these two changes, lets see how Kaleidoscope works now! -->

```bash
ready> 4+5;
Read top-level expression:
define double @0() {
entry:
  ret double 9.000000e+00
}

Evaluated to 9.000000
```

现在看起来基本能工作了。函数的dump显示“no argument function that always returns double”

Well this looks like it is basically working. The dump of the function shows the “no argument function that always returns double” that we synthesize for each top-level expression that is typed in. This demonstrates very basic functionality, but can we do more?

```bash
ready> def testfunc(x y) x + y*2;
Read function definition:
define double @testfunc(double %x, double %y) {
entry:
  %multmp = fmul double %y, 2.000000e+00
  %addtmp = fadd double %multmp, %x
  ret double %addtmp
}

ready> testfunc(4, 10);
Read top-level expression:
define double @1() {
entry:
  %calltmp = call double @testfunc(double 4.000000e+00, double 1.000000e+01)
  ret double %calltmp
}

Evaluated to 24.000000

ready> testfunc(5, 10);
ready> LLVM ERROR: Program used external function 'testfunc' which could not be resolved!
```

函数定义和调用也都成功了，但是最后一行有一个ERROR。这个调用看起来是合法的，到底发生了什么呢？可能你已经从API中猜到了，一个module是JIT分配的一个单元，testfunc是这个module的一部分，包含了一个匿名表达式。当我们从JIT中移除了这个module，并且释放了这个匿名表达式的内存后，我们同时也删除了testfunc的定义。然后，当我们试着第二次调用`testfunc`时，JIT就找不到它了。

<!-- Function definitions and calls also work, but something went very wrong on that last line. The call looks valid, so what happened? As you may have guessed from the the API a Module is a unit of allocation for the JIT, and testfunc was part of the same module that contained anonymous expression. When we removed that module from the JIT to free the memory for the anonymous expression, we deleted the definition of testfunc along with it. Then, when we tried to call `testfunc` a second time, the JIT could no longer find it. -->

解决这个ERROR最简单的办法是将这个匿名表达式放在一个和其他函数定义分开的单独的module中。JIT可以很轻松的处理跨module的函数调用，只要每个被调用的函数都有函数原型，并且在被调用前添加到JIT中。将匿名表达式放在一个不同的module中，我们可以在不影响其他函数的情况下删除它。

<!-- The easiest way to fix this is to put the anonymous expression in a separate module from the rest of the function definitions. The JIT will happily resolve function calls across module boundaries, as long as each of the functions called has a prototype, and is added to the JIT before it is called. By putting the anonymous expression in a different module we can delete it without affecting the rest of the functions. -->

实际上，进一步我们将把每一个函数放到一个单独的module中。这样做可以为KaleidoscopeJIT开发出一个有用的特性，让我们的环境更像一个交互式解释器环境（REPL）：函数可以被多次添加到JIT（不像一个module中所有函数的定义都不能相同）。当你在KaleidoscopeJIT中查找一个symbol时，它总会返回最新的定义：

<!-- In fact, we’re going to go a step further and put every function in its own module. Doing so allows us to exploit a useful property of the KaleidoscopeJIT that will make our environment more REPL-like: Functions can be added to the JIT more than once (unlike a module where every function must have a unique definition). When you look up a symbol in KaleidoscopeJIT it will always return the most recent definition: -->

```bash
ready> def foo(x) x + 1;
Read function definition:
define double @foo(double %x) {
entry:
  %addtmp = fadd double %x, 1.000000e+00
  ret double %addtmp
}

ready> foo(2);
Evaluated to 3.000000

ready> def foo(x) x + 2;
define double @foo(double %x) {
entry:
  %addtmp = fadd double %x, 2.000000e+00
  ret double %addtmp
}

ready> foo(2);
Evaluated to 4.000000
```

为了允许每个函数都能保存在单独的module中，我们需要在每个打开的新module中重新创建之前函数的声明。

<!-- To allow each function to live in its own module we’ll need a way to re-generate previous function declarations into each new module we open: -->

```C++
static std::unique_ptr<KaleidoscopeJIT> TheJIT;

...

Function *getFunction(std::string Name) {
  // First, see if the function has already been added to the current module.
  if (auto *F = TheModule->getFunction(Name))
    return F;

  // If not, check whether we can codegen the declaration from some existing
  // prototype.
  auto FI = FunctionProtos.find(Name);
  if (FI != FunctionProtos.end())
    return FI->second->codegen();

  // If no existing prototype exists, return null.
  return nullptr;
}

...

Value *CallExprAST::codegen() {
  // Look up the name in the global module table.
  Function *CalleeF = getFunction(Callee);

...

Function *FunctionAST::codegen() {
  // Transfer ownership of the prototype to the FunctionProtos map, but keep a
  // reference to it for use below.
  auto &P = *Proto;
  FunctionProtos[Proto->getName()] = std::move(Proto);
  Function *TheFunction = getFunction(P.getName());
  if (!TheFunction)
    return nullptr;
```

为此，我们首先要增加一个新的全局变量`FunctionProtos`，它保存了每个函数的最新的函数原型。为了方便实用，我们将增加一个新的方法`getFunction()`，来代替`TheModule->getFunction()`的调用。这个新方法会在`TheModule`中搜索已经存在的函数声明，如果没有找到的话，会从FunctionProtos中生成一个新的声明。在`CallExprAST::codegen()`中，我们只需要替换`TheModule->getFunction()`。在`FunctionAST::codegen()`中，我们首先需要更新FunctionProtos map，然后调用`getFunction()`。这些做完之后，我们就可以在当前module中获取任意之前声明的函数的函数声明了。

<!-- To enable this, we’ll start by adding a new global, `FunctionProtos`, that holds the most recent prototype for each function. We’ll also add a convenience method, `getFunction()`, to replace calls to `TheModule->getFunction()`. Our convenience method searches `TheModule` for an existing function declaration, falling back to generating a new declaration from FunctionProtos if it doesn’t find one. In `CallExprAST::codegen()` we just need to replace the call to `TheModule->getFunction()`. In `FunctionAST::codegen()` we need to update the FunctionProtos map first, then call `getFunction()`. With this done, we can always obtain a function declaration in the current module for any previously declared function. -->

我们还需要更新HandleDefinition和HandleExtern：

<!-- We also need to update HandleDefinition and HandleExtern: -->

```C++
static void HandleDefinition() {
  if (auto FnAST = ParseDefinition()) {
    if (auto *FnIR = FnAST->codegen()) {
      fprintf(stderr, "Read function definition:");
      FnIR->print(errs());
      fprintf(stderr, "\n");
      TheJIT->addModule(std::move(TheModule));
      InitializeModuleAndPassManager();
    }
  } else {
    // Skip token for error recovery.
     getNextToken();
  }
}

static void HandleExtern() {
  if (auto ProtoAST = ParseExtern()) {
    if (auto *FnIR = ProtoAST->codegen()) {
      fprintf(stderr, "Read extern: ");
      FnIR->print(errs());
      fprintf(stderr, "\n");
      FunctionProtos[ProtoAST->getName()] = std::move(ProtoAST);
    }
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}
```

在HandleDefinition中，我们增加了两行，将新定义的函数转移到JIT中，并打开一个新的module。在HandleExtern中，我们只增加了一行，将函数原型添加到FunctionProtos中。

<!-- In HandleDefinition, we add two lines to transfer the newly defined function to the JIT and open a new module. In HandleExtern, we just need to add one line to add the prototype to FunctionProtos. -->

这些做完后，让我们再试一次我们的交互式解释器环境（REPL）（这次我们没有显示匿名函数的dump，你应该可以自己想到结果）：

<!-- With these changes made, lets try our REPL again (I removed the dump of the anonymous functions this time, you should get the idea by now :) : -->

```bash
ready> def foo(x) x + 1;
ready> foo(2);
Evaluated to 3.000000

ready> def foo(x) x + 2;
ready> foo(2);
Evaluated to 4.000000
```

成功了！

<!-- It works! -->

即使是这样简单的代码，我们也可以获得令人惊讶的强大的处理能力，试试这些例子：

<!-- Even with this simple code, we get some surprisingly powerful capabilities - check this out: -->

```bash
ready> extern sin(x);
Read extern:
declare double @sin(double)

ready> extern cos(x);
Read extern:
declare double @cos(double)

ready> sin(1.0);
Read top-level expression:
define double @2() {
entry:
  ret double 0x3FEAED548F090CEE
}

Evaluated to 0.841471

ready> def foo(x) sin(x)*sin(x) + cos(x)*cos(x);
Read function definition:
define double @foo(double %x) {
entry:
  %calltmp = call double @sin(double %x)
  %multmp = fmul double %calltmp, %calltmp
  %calltmp2 = call double @cos(double %x)
  %multmp4 = fmul double %calltmp2, %calltmp2
  %addtmp = fadd double %multmp, %multmp4
  ret double %addtmp
}

ready> foo(4.0);
Read top-level expression:
define double @3() {
entry:
  %calltmp = call double @foo(double 4.000000e+00)
  ret double %calltmp
}

Evaluated to 1.000000
```

哇哦，JIT是怎么知道sin和cos的呢？答案惊人的简单：KaleidoscopeJIT有一个直观的，用来寻找不在任何module中symbol的规则：首先，在添加到JIT的所有module中搜索，按从最新到最旧的顺序，找最新的定义。如果在JIT中没找到，会在Kaleidoscope进程调用“`dlsym("sin")`”。因为“`sin`”在JIT的地址空间被定义，it simply patches up calls in the module to call the libm version of `sin` directly. But in some cases this even goes further: as sin and cos are names of standard math functions, the constant folder will directly evaluate the function calls to the correct result when called with constants like in the “`sin(1.0)`” above.

<!-- Whoa, how does the JIT know about sin and cos? The answer is surprisingly simple: The KaleidoscopeJIT has a straightforward symbol resolution rule that it uses to find symbols that aren’t available in any given module: First it searches all the modules that have already been added to the JIT, from the most recent to the oldest, to find the newest definition. If no definition is found inside the JIT, it falls back to calling “`dlsym("sin")`” on the Kaleidoscope process itself. Since “`sin`” is defined within the JIT’s address space, it simply patches up calls in the module to call the libm version of `sin` directly. But in some cases this even goes further: as sin and cos are names of standard math functions, the constant folder will directly evaluate the function calls to the correct result when called with constants like in the “`sin(1.0)`” above. -->

未来我们将会看到如何对这些symbol处理规则进行微调，生成各种有用的特性，从安全型（限制JIT编译的代码中，可访问的symbol集合），到基于symbol名的动态代码生成，甚至lazy编译。

<!-- In the future we’ll see how tweaking this symbol resolution rule can be used to enable all sorts of useful features, from security (restricting the set of symbols available to JIT’d code), to dynamic code generation based on symbol names, and even lazy compilation. -->

symbol resolution rule最直接的一个好处是我们现在可以通过编写C++代码来实现运算符，扩展这门语言。举例来说，如果我们添加：

<!-- One immediate benefit of the symbol resolution rule is that we can now extend the language by writing arbitrary C++ code to implement operations. For example, if we add: -->

```C++
#ifdef LLVM_ON_WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

/// putchard - putchar that takes a double and returns 0.
extern "C" DLLEXPORT double putchard(double X) {
  fputc((char)X, stderr);
  return 0;
}
```

注意，在Windows系统中，我们需要实际地导出函数，因为动态符号加载器将使用GetProcAddress来查找symbols。

<!-- Note, that for Windows we need to actually export the functions because the dynamic symbol loader will use GetProcAddress to find the symbols. -->

现在我们可以用类似“`extern putchard(x); putchard(120);`”的语句来向控制台做简单的输出了，这条语句会在控制台打印一个小写的‘x’（120是‘x’的ASCII码）。相似的代码可以用来实现文件I/O，控制台输入，以及Kaleidoscope的许多其它功能。

<!-- Now we can produce simple output to the console by using things like: “`extern putchard(x); putchard(120);`”, which prints a lowercase ‘x’ on the console (120 is the ASCII code for ‘x’). Similar code could be used to implement file I/O, console input, and many other capabilities in Kaleidoscope. -->

至此，Kaleidoscope教程的JIT和优化器章节就结束了。现在，我们可以编译一门非图灵完备（non-Turing-complete）的编程语言，优化并在用户驱动下即时编译它。下面我们将进入[extending the language with control flow constructs](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl05.html)，在探索的过程中解决LLVM IR的一些有趣的问题。

<!-- This completes the JIT and optimizer chapter of the Kaleidoscope tutorial. At this point, we can compile a non-Turing-complete programming language, optimize and JIT compile it in a user-driven way. Next up we’ll look into [extending the language with control flow constructs](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl05.html), tackling some interesting LLVM IR issues along the way. -->

## 4.5. Full Code Listing

这里是我们的例子的完整的，增加了LLVM JIT和优化器之后的代码。用下面的指令build这个例子：

<!-- Here is the complete code listing for our running example, enhanced with the LLVM JIT and optimizer. To build this example, use: -->

```bash
# Compile
clang++ -g toy.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core mcjit native` -O3 -o toy
# Run
./toy
```

如果你在Linux系统下编译，请额外添加了“-rdynamic”选项。这个选项可以确保在运行时，外部函数被正确处理。

<!-- If you are compiling this on Linux, make sure to add the “-rdynamic” option as well. This makes sure that the external functions are resolved properly at runtime. -->

下面是代码：

<!--Here is the code:-->

```C++
#include "llvm/ADT/APFloat.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Target/TargetMachine.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/Scalar/GVN.h"
#include "../include/KaleidoscopeJIT.h"
#include <algorithm>
#include <cassert>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <memory>
#include <string>
#include <vector>

using namespace llvm;
using namespace llvm::orc;

//===----------------------------------------------------------------------===//
// Lexer
//===----------------------------------------------------------------------===//

// The lexer returns tokens [0-255] if it is an unknown character, otherwise one
// of these for known things.
enum Token {
  tok_eof = -1,

  // commands
  tok_def = -2,
  tok_extern = -3,

  // primary
  tok_identifier = -4,
  tok_number = -5
};

static std::string IdentifierStr; // Filled in if tok_identifier
static double NumVal;             // Filled in if tok_number

/// gettok - Return the next token from standard input.
static int gettok() {
  static int LastChar = ' ';

  // Skip any whitespace.
  while (isspace(LastChar))
    LastChar = getchar();

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

  if (isdigit(LastChar) || LastChar == '.') { // Number: [0-9.]+
    std::string NumStr;
    do {
      NumStr += LastChar;
      LastChar = getchar();
    } while (isdigit(LastChar) || LastChar == '.');

    NumVal = strtod(NumStr.c_str(), nullptr);
    return tok_number;
  }

  if (LastChar == '#') {
    // Comment until end of line.
    do
      LastChar = getchar();
    while (LastChar != EOF && LastChar != '\n' && LastChar != '\r');

    if (LastChar != EOF)
      return gettok();
  }

  // Check for end of file.  Don't eat the EOF.
  if (LastChar == EOF)
    return tok_eof;

  // Otherwise, just return the character as its ascii value.
  int ThisChar = LastChar;
  LastChar = getchar();
  return ThisChar;
}

//===----------------------------------------------------------------------===//
// Abstract Syntax Tree (aka Parse Tree)
//===----------------------------------------------------------------------===//

namespace {

/// ExprAST - Base class for all expression nodes.
class ExprAST {
public:
  virtual ~ExprAST() = default;

  virtual Value *codegen() = 0;
};

/// NumberExprAST - Expression class for numeric literals like "1.0".
class NumberExprAST : public ExprAST {
  double Val;

public:
  NumberExprAST(double Val) : Val(Val) {}

  Value *codegen() override;
};

/// VariableExprAST - Expression class for referencing a variable, like "a".
class VariableExprAST : public ExprAST {
  std::string Name;

public:
  VariableExprAST(const std::string &Name) : Name(Name) {}

  Value *codegen() override;
};

/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
  char Op;
  std::unique_ptr<ExprAST> LHS, RHS;

public:
  BinaryExprAST(char Op, std::unique_ptr<ExprAST> LHS,
                std::unique_ptr<ExprAST> RHS)
      : Op(Op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}

  Value *codegen() override;
};

/// CallExprAST - Expression class for function calls.
class CallExprAST : public ExprAST {
  std::string Callee;
  std::vector<std::unique_ptr<ExprAST>> Args;

public:
  CallExprAST(const std::string &Callee,
              std::vector<std::unique_ptr<ExprAST>> Args)
      : Callee(Callee), Args(std::move(Args)) {}

  Value *codegen() override;
};

/// PrototypeAST - This class represents the "prototype" for a function,
/// which captures its name, and its argument names (thus implicitly the number
/// of arguments the function takes).
class PrototypeAST {
  std::string Name;
  std::vector<std::string> Args;

public:
  PrototypeAST(const std::string &Name, std::vector<std::string> Args)
      : Name(Name), Args(std::move(Args)) {}

  Function *codegen();
  const std::string &getName() const { return Name; }
};

/// FunctionAST - This class represents a function definition itself.
class FunctionAST {
  std::unique_ptr<PrototypeAST> Proto;
  std::unique_ptr<ExprAST> Body;

public:
  FunctionAST(std::unique_ptr<PrototypeAST> Proto,
              std::unique_ptr<ExprAST> Body)
      : Proto(std::move(Proto)), Body(std::move(Body)) {}

  Function *codegen();
};

} // end anonymous namespace

//===----------------------------------------------------------------------===//
// Parser
//===----------------------------------------------------------------------===//

/// CurTok/getNextToken - Provide a simple token buffer.  CurTok is the current
/// token the parser is looking at.  getNextToken reads another token from the
/// lexer and updates CurTok with its results.
static int CurTok;
static int getNextToken() { return CurTok = gettok(); }

/// BinopPrecedence - This holds the precedence for each binary operator that is
/// defined.
static std::map<char, int> BinopPrecedence;

/// GetTokPrecedence - Get the precedence of the pending binary operator token.
static int GetTokPrecedence() {
  if (!isascii(CurTok))
    return -1;

  // Make sure it's a declared binop.
  int TokPrec = BinopPrecedence[CurTok];
  if (TokPrec <= 0)
    return -1;
  return TokPrec;
}

/// LogError* - These are little helper functions for error handling.
std::unique_ptr<ExprAST> LogError(const char *Str) {
  fprintf(stderr, "Error: %s\n", Str);
  return nullptr;
}

std::unique_ptr<PrototypeAST> LogErrorP(const char *Str) {
  LogError(Str);
  return nullptr;
}

static std::unique_ptr<ExprAST> ParseExpression();

/// numberexpr ::= number
static std::unique_ptr<ExprAST> ParseNumberExpr() {
  auto Result = llvm::make_unique<NumberExprAST>(NumVal);
  getNextToken(); // consume the number
  return std::move(Result);
}

/// parenexpr ::= '(' expression ')'
static std::unique_ptr<ExprAST> ParseParenExpr() {
  getNextToken(); // eat (.
  auto V = ParseExpression();
  if (!V)
    return nullptr;

  if (CurTok != ')')
    return LogError("expected ')'");
  getNextToken(); // eat ).
  return V;
}

/// identifierexpr
///   ::= identifier
///   ::= identifier '(' expression* ')'
static std::unique_ptr<ExprAST> ParseIdentifierExpr() {
  std::string IdName = IdentifierStr;

  getNextToken(); // eat identifier.

  if (CurTok != '(') // Simple variable ref.
    return llvm::make_unique<VariableExprAST>(IdName);

  // Call.
  getNextToken(); // eat (
  std::vector<std::unique_ptr<ExprAST>> Args;
  if (CurTok != ')') {
    while (true) {
      if (auto Arg = ParseExpression())
        Args.push_back(std::move(Arg));
      else
        return nullptr;

      if (CurTok == ')')
        break;

      if (CurTok != ',')
        return LogError("Expected ')' or ',' in argument list");
      getNextToken();
    }
  }

  // Eat the ')'.
  getNextToken();

  return llvm::make_unique<CallExprAST>(IdName, std::move(Args));
}

/// primary
///   ::= identifierexpr
///   ::= numberexpr
///   ::= parenexpr
static std::unique_ptr<ExprAST> ParsePrimary() {
  switch (CurTok) {
  default:
    return LogError("unknown token when expecting an expression");
  case tok_identifier:
    return ParseIdentifierExpr();
  case tok_number:
    return ParseNumberExpr();
  case '(':
    return ParseParenExpr();
  }
}

/// binoprhs
///   ::= ('+' primary)*
static std::unique_ptr<ExprAST> ParseBinOpRHS(int ExprPrec,
                                              std::unique_ptr<ExprAST> LHS) {
  // If this is a binop, find its precedence.
  while (true) {
    int TokPrec = GetTokPrecedence();

    // If this is a binop that binds at least as tightly as the current binop,
    // consume it, otherwise we are done.
    if (TokPrec < ExprPrec)
      return LHS;

    // Okay, we know this is a binop.
    int BinOp = CurTok;
    getNextToken(); // eat binop

    // Parse the primary expression after the binary operator.
    auto RHS = ParsePrimary();
    if (!RHS)
      return nullptr;

    // If BinOp binds less tightly with RHS than the operator after RHS, let
    // the pending operator take RHS as its LHS.
    int NextPrec = GetTokPrecedence();
    if (TokPrec < NextPrec) {
      RHS = ParseBinOpRHS(TokPrec + 1, std::move(RHS));
      if (!RHS)
        return nullptr;
    }

    // Merge LHS/RHS.
    LHS =
        llvm::make_unique<BinaryExprAST>(BinOp, std::move(LHS), std::move(RHS));
  }
}

/// expression
///   ::= primary binoprhs
///
static std::unique_ptr<ExprAST> ParseExpression() {
  auto LHS = ParsePrimary();
  if (!LHS)
    return nullptr;

  return ParseBinOpRHS(0, std::move(LHS));
}

/// prototype
///   ::= id '(' id* ')'
static std::unique_ptr<PrototypeAST> ParsePrototype() {
  if (CurTok != tok_identifier)
    return LogErrorP("Expected function name in prototype");

  std::string FnName = IdentifierStr;
  getNextToken();

  if (CurTok != '(')
    return LogErrorP("Expected '(' in prototype");

  std::vector<std::string> ArgNames;
  while (getNextToken() == tok_identifier)
    ArgNames.push_back(IdentifierStr);
  if (CurTok != ')')
    return LogErrorP("Expected ')' in prototype");

  // success.
  getNextToken(); // eat ')'.

  return llvm::make_unique<PrototypeAST>(FnName, std::move(ArgNames));
}

/// definition ::= 'def' prototype expression
static std::unique_ptr<FunctionAST> ParseDefinition() {
  getNextToken(); // eat def.
  auto Proto = ParsePrototype();
  if (!Proto)
    return nullptr;

  if (auto E = ParseExpression())
    return llvm::make_unique<FunctionAST>(std::move(Proto), std::move(E));
  return nullptr;
}

/// toplevelexpr ::= expression
static std::unique_ptr<FunctionAST> ParseTopLevelExpr() {
  if (auto E = ParseExpression()) {
    // Make an anonymous proto.
    auto Proto = llvm::make_unique<PrototypeAST>("__anon_expr",
                                                 std::vector<std::string>());
    return llvm::make_unique<FunctionAST>(std::move(Proto), std::move(E));
  }
  return nullptr;
}

/// external ::= 'extern' prototype
static std::unique_ptr<PrototypeAST> ParseExtern() {
  getNextToken(); // eat extern.
  return ParsePrototype();
}

//===----------------------------------------------------------------------===//
// Code Generation
//===----------------------------------------------------------------------===//

static LLVMContext TheContext;
static IRBuilder<> Builder(TheContext);
static std::unique_ptr<Module> TheModule;
static std::map<std::string, Value *> NamedValues;
static std::unique_ptr<legacy::FunctionPassManager> TheFPM;
static std::unique_ptr<KaleidoscopeJIT> TheJIT;
static std::map<std::string, std::unique_ptr<PrototypeAST>> FunctionProtos;

Value *LogErrorV(const char *Str) {
  LogError(Str);
  return nullptr;
}

Function *getFunction(std::string Name) {
  // First, see if the function has already been added to the current module.
  if (auto *F = TheModule->getFunction(Name))
    return F;

  // If not, check whether we can codegen the declaration from some existing
  // prototype.
  auto FI = FunctionProtos.find(Name);
  if (FI != FunctionProtos.end())
    return FI->second->codegen();

  // If no existing prototype exists, return null.
  return nullptr;
}

Value *NumberExprAST::codegen() {
  return ConstantFP::get(TheContext, APFloat(Val));
}

Value *VariableExprAST::codegen() {
  // Look this variable up in the function.
  Value *V = NamedValues[Name];
  if (!V)
    return LogErrorV("Unknown variable name");
  return V;
}

Value *BinaryExprAST::codegen() {
  Value *L = LHS->codegen();
  Value *R = RHS->codegen();
  if (!L || !R)
    return nullptr;

  switch (Op) {
  case '+':
    return Builder.CreateFAdd(L, R, "addtmp");
  case '-':
    return Builder.CreateFSub(L, R, "subtmp");
  case '*':
    return Builder.CreateFMul(L, R, "multmp");
  case '<':
    L = Builder.CreateFCmpULT(L, R, "cmptmp");
    // Convert bool 0/1 to double 0.0 or 1.0
    return Builder.CreateUIToFP(L, Type::getDoubleTy(TheContext), "booltmp");
  default:
    return LogErrorV("invalid binary operator");
  }
}

Value *CallExprAST::codegen() {
  // Look up the name in the global module table.
  Function *CalleeF = getFunction(Callee);
  if (!CalleeF)
    return LogErrorV("Unknown function referenced");

  // If argument mismatch error.
  if (CalleeF->arg_size() != Args.size())
    return LogErrorV("Incorrect # arguments passed");

  std::vector<Value *> ArgsV;
  for (unsigned i = 0, e = Args.size(); i != e; ++i) {
    ArgsV.push_back(Args[i]->codegen());
    if (!ArgsV.back())
      return nullptr;
  }

  return Builder.CreateCall(CalleeF, ArgsV, "calltmp");
}

Function *PrototypeAST::codegen() {
  // Make the function type:  double(double,double) etc.
  std::vector<Type *> Doubles(Args.size(), Type::getDoubleTy(TheContext));
  FunctionType *FT =
      FunctionType::get(Type::getDoubleTy(TheContext), Doubles, false);

  Function *F =
      Function::Create(FT, Function::ExternalLinkage, Name, TheModule.get());

  // Set names for all arguments.
  unsigned Idx = 0;
  for (auto &Arg : F->args())
    Arg.setName(Args[Idx++]);

  return F;
}

Function *FunctionAST::codegen() {
  // Transfer ownership of the prototype to the FunctionProtos map, but keep a
  // reference to it for use below.
  auto &P = *Proto;
  FunctionProtos[Proto->getName()] = std::move(Proto);
  Function *TheFunction = getFunction(P.getName());
  if (!TheFunction)
    return nullptr;

  // Create a new basic block to start insertion into.
  BasicBlock *BB = BasicBlock::Create(TheContext, "entry", TheFunction);
  Builder.SetInsertPoint(BB);

  // Record the function arguments in the NamedValues map.
  NamedValues.clear();
  for (auto &Arg : TheFunction->args())
    NamedValues[Arg.getName()] = &Arg;

  if (Value *RetVal = Body->codegen()) {
    // Finish off the function.
    Builder.CreateRet(RetVal);

    // Validate the generated code, checking for consistency.
    verifyFunction(*TheFunction);

    // Run the optimizer on the function.
    TheFPM->run(*TheFunction);

    return TheFunction;
  }

  // Error reading body, remove function.
  TheFunction->eraseFromParent();
  return nullptr;
}

//===----------------------------------------------------------------------===//
// Top-Level parsing and JIT Driver
//===----------------------------------------------------------------------===//

static void InitializeModuleAndPassManager() {
  // Open a new module.
  TheModule = llvm::make_unique<Module>("my cool jit", TheContext);
  TheModule->setDataLayout(TheJIT->getTargetMachine().createDataLayout());

  // Create a new pass manager attached to it.
  TheFPM = llvm::make_unique<legacy::FunctionPassManager>(TheModule.get());

  // Do simple "peephole" optimizations and bit-twiddling optzns.
  TheFPM->add(createInstructionCombiningPass());
  // Reassociate expressions.
  TheFPM->add(createReassociatePass());
  // Eliminate Common SubExpressions.
  TheFPM->add(createGVNPass());
  // Simplify the control flow graph (deleting unreachable blocks, etc).
  TheFPM->add(createCFGSimplificationPass());

  TheFPM->doInitialization();
}

static void HandleDefinition() {
  if (auto FnAST = ParseDefinition()) {
    if (auto *FnIR = FnAST->codegen()) {
      fprintf(stderr, "Read function definition:");
      FnIR->print(errs());
      fprintf(stderr, "\n");
      TheJIT->addModule(std::move(TheModule));
      InitializeModuleAndPassManager();
    }
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}

static void HandleExtern() {
  if (auto ProtoAST = ParseExtern()) {
    if (auto *FnIR = ProtoAST->codegen()) {
      fprintf(stderr, "Read extern: ");
      FnIR->print(errs());
      fprintf(stderr, "\n");
      FunctionProtos[ProtoAST->getName()] = std::move(ProtoAST);
    }
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}

static void HandleTopLevelExpression() {
  // Evaluate a top-level expression into an anonymous function.
  if (auto FnAST = ParseTopLevelExpr()) {
    if (FnAST->codegen()) {
      // JIT the module containing the anonymous expression, keeping a handle so
      // we can free it later.
      auto H = TheJIT->addModule(std::move(TheModule));
      InitializeModuleAndPassManager();

      // Search the JIT for the __anon_expr symbol.
      auto ExprSymbol = TheJIT->findSymbol("__anon_expr");
      assert(ExprSymbol && "Function not found");

      // Get the symbol's address and cast it to the right type (takes no
      // arguments, returns a double) so we can call it as a native function.
      double (*FP)() = (double (*)())(intptr_t)cantFail(ExprSymbol.getAddress());
      fprintf(stderr, "Evaluated to %f\n", FP());

      // Delete the anonymous expression module from the JIT.
      TheJIT->removeModule(H);
    }
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}

/// top ::= definition | external | expression | ';'
static void MainLoop() {
  while (true) {
    fprintf(stderr, "ready> ");
    switch (CurTok) {
    case tok_eof:
      return;
    case ';': // ignore top-level semicolons.
      getNextToken();
      break;
    case tok_def:
      HandleDefinition();
      break;
    case tok_extern:
      HandleExtern();
      break;
    default:
      HandleTopLevelExpression();
      break;
    }
  }
}

//===----------------------------------------------------------------------===//
// "Library" functions that can be "extern'd" from user code.
//===----------------------------------------------------------------------===//

#ifdef LLVM_ON_WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

/// putchard - putchar that takes a double and returns 0.
extern "C" DLLEXPORT double putchard(double X) {
  fputc((char)X, stderr);
  return 0;
}

/// printd - printf that takes a double prints it as "%f\n", returning 0.
extern "C" DLLEXPORT double printd(double X) {
  fprintf(stderr, "%f\n", X);
  return 0;
}

//===----------------------------------------------------------------------===//
// Main driver code.
//===----------------------------------------------------------------------===//

int main() {
  InitializeNativeTarget();
  InitializeNativeTargetAsmPrinter();
  InitializeNativeTargetAsmParser();

  // Install standard binary operators.
  // 1 is lowest precedence.
  BinopPrecedence['<'] = 10;
  BinopPrecedence['+'] = 20;
  BinopPrecedence['-'] = 20;
  BinopPrecedence['*'] = 40; // highest.

  // Prime the first token.
  fprintf(stderr, "ready> ");
  getNextToken();

  TheJIT = llvm::make_unique<KaleidoscopeJIT>();

  InitializeModuleAndPassManager();

  // Run the main "interpreter loop" now.
  MainLoop();

  return 0;
}
```
