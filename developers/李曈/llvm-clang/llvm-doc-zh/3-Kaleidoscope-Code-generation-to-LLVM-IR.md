---
title: '3. Kaleidoscope: Code generation to LLVM IR'
date: 2018-01-11 11:34:44
tags: LLVM Tutorial
---

## 3.1. Chapter 3 Introduction

欢迎来到[用LLVM实现一门编程语言](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)教程第3章。这一章将会为你展示如何把第2章介绍的[抽象语法树](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl02.html)转变为LLVM IR。这些内容会教给你一些LLVM做事情的方法，并向你展示LLVM非常易用。相比于生成LLVM IR code，构造词法分析器和语法分析器的工作量大很多。

<!-- more -->

<!-- Welcome to Chapter 3 of the “[Implementing a language with LLVM](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)” tutorial. This chapter shows you how to transform the [Abstract Syntax Tree](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl02.html), built in Chapter 2, into LLVM IR. This will teach you a little bit about how LLVM does things, as well as demonstrate how easy it is to use. It’s much more work to build a lexer and parser than it is to generate LLVM IR code.-->

**注意**：这一章的代码需要LLVM 3.7或者更高版本，LLVM 3.6以及更低版本的不能运行这一章的代码。同时，你需要使用和你的LLVM版本对应的教程版本，如果你在使用官方的LLVM release，请使用在你的release中包含的文档，或者在[llvm.org releases page](http://llvm.org/releases/)寻找对应的文档。

<!-- **Please note**: the code in this chapter and later require LLVM 3.7 or later. LLVM 3.6 and before will not work with it. Also note that you need to use a version of this tutorial that matches your LLVM release: If you are using an official LLVM release, use the version of the documentation included with your release or on the [llvm.org releases page](http://llvm.org/releases/). -->

## 3.2. Code Generation Setup

为了生成LLVM IR，我们需要先进行一些简单的操作。首先，我们在每个AST类里定义了一个虚函数——代码生成器`codegen`方法。

<!-- In order to generate LLVM IR, we want some simple setup to get started. First we define virtual code generation (codegen) methods in each AST class: -->

```C++
/// ExprAST - Base class for all expression nodes.
class ExprAST {
public:
  virtual ~ExprAST() {}
  virtual Value *codegen() = 0;
};

/// NumberExprAST - Expression class for numeric literals like "1.0".
class NumberExprAST : public ExprAST {
  double Val;

public:
  NumberExprAST(double Val) : Val(Val) {}
  virtual Value *codegen();
};
...
```

`codegen()`方法用来生成所在的AST节点以及它依赖的所有东西的IR，所有的`codegen()`都会返回一个LLVM Value对象。"Value"是用来表示一个LLVM中的[静态单赋值(SSA)注册器](http://en.wikipedia.org/wiki/Static_single_assignment_form)，或者叫"SSA value"。SSA value最独特的一点是变量的值只要在执行和它相关的指令是才会被计算，而且在和它相关的指令再次执行前，它的值不会被更新。换句话说，SSA value是“固定的”。更多相关知识，请阅读[Static Single Assignment](http://en.wikipedia.org/wiki/Static_single_assignment_form)，当你理解后，你就会发现这个概念非常的自然。

<!-- The codegen() method says to emit IR for that AST node along with all the things it depends on, and they all return an LLVM Value object. “Value” is the class used to represent a “[Static Single Assignment (SSA) register](http://en.wikipedia.org/wiki/Static_single_assignment_form)” or “SSA value” in LLVM. The most distinct aspect of SSA values is that their value is computed as the related instruction executes, and it does not get a new value until (and if) the instruction re-executes. In other words, there is no way to “change” an SSA value. For more information, please read up on [Static Single Assignment](http://en.wikipedia.org/wiki/Static_single_assignment_form) - the concepts are really quite natural once you grok them. -->

注意，除了在ExprAST类的继承体系中添加虚函数这种方案，你还可以使用[visitor pattern](http://en.wikipedia.org/wiki/Visitor_pattern)或者其他方案去做这件事情。再强调一次，这篇教程并不是一个好的软件工程实践，我们的目标是尽量简化不必要的学习，让你专注于LLVM，所以针对这个目标，虚函数是一个简单的方案。

<!-- Note that instead of adding virtual methods to the ExprAST class hierarchy, it could also make sense to use a [visitor pattern](http://en.wikipedia.org/wiki/Visitor_pattern) or some other way to model this. Again, this tutorial won’t dwell on good software engineering practices: for our purposes, adding a virtual method is simplest. -->

我们要做的第二件事情是增加一个“LogError”方法，用在语法分析上，在代码生成阶段用来报错（比如说，使用未定义的参数）：

<!-- The second thing we want is an “LogError” method like we used for the parser, which will be used to report errors found during code generation (for example, use of an undeclared parameter): -->

```C++
static LLVMContext TheContext;
static IRBuilder<> Builder(TheContext);
static std::unique_ptr<Module> TheModule;
static std::map<std::string, Value *> NamedValues;

Value *LogErrorV(const char *Str) {
  LogError(Str);
  return nullptr;
}
```

这些静态变量将会在代码生成阶段使用。`TheContext`是一个不透明的对象，保存着很多LLVM核心数据结构，比如数据类型和constant值的表。我们不需要从细节上理解它，我们只需要一个实例，用来传递给需要这个实例的APIs。

<!-- The static variables will be used during code generation. `TheContext` is an opaque object that owns a lot of core LLVM data structures, such as the type and constant value tables. We don’t need to understand it in detail, we just need a single instance to pass into APIs that require it. -->

`Builder`对象是一个很有帮助的对象，让生成LLVM指令更加方便。[IRBuilder](http://llvm.org/doxygen/IRBuilder_8h-source.html)类模版的实例会跟踪当前要插入指令的位置，同时有创建新指令的方法可以调用。

<!-- The `Builder` object is a helper object that makes it easy to generate LLVM instructions. Instances of the [IRBuilder](http://llvm.org/doxygen/IRBuilder_8h-source.html) class template keep track of the current place to insert instructions and has methods to create new instructions. -->

`TheModule`是一个LLVM的construct，包含了函数和全局变量。在许多方面，它是LLVM IR用来包含代码的顶层结构体。它还包含了存储我们生成的IR的内存，所以codegen()方法返回的是原始的Value\*，而不是一个unique_ptr\<Value\>。

<!-- `TheModule` is an LLVM construct that contains functions and global variables. In many ways, it is the top-level structure that the LLVM IR uses to contain code. It will own the memory for all of the IR that we generate, which is why the codegen() method returns a raw Value\*, rather than a unique_ptr\<Value\>. -->

`NamedValues` map保存了当前作用域里，定义了哪些变量，以及它们的LLVM表示是什么。（换句话说，这是一个代码的符号表）。在Kaleidoscope的格式中，它们唯一可以被引用的东西是函数参数。这样一来，在为它们的函数体生成代码后，函数的参数就会保存在这个map中。

<!-- The `NamedValues` map keeps track of which values are defined in the current scope and what their LLVM representation is. (In other words, it is a symbol table for the code). In this form of Kaleidoscope, the only things that can be referenced are function parameters. As such, function parameters will be in this map when generating code for their function body. -->

有了这些基础，我们可以开始讨论如何为每个表达式生成代码了。注意，我们假设`Builder`已经设置好，可以生成代码。现在，我们将会假设这些都已经完成了，我们会用它来生成代码。

<!-- With these basics in place, we can start talking about how to generate code for each expression. Note that this assumes that the `Builder` has been set up to generate code into something. For now, we’ll assume that this has already been done, and we’ll just use it to emit code. -->

## 3.3. Expression Code Generation

生成表达式节点的LLVM code非常直观：对于全部的四种表达式节点，只需要不到45行的带注释的代码。首先，我们处理数值字面量：

<!--Generating LLVM code for expression nodes is very straightforward: less than 45 lines of commented code for all four of our expression nodes. First we’ll do numeric literals:-->

```C++
Value *NumberExprAST::codegen() {
  return ConstantFP::get(TheContext, APFloat(Val));
}
```

在LLVM IR中，数值固定量用`ConstantFP`类来表示，类中有一个`APFloat`变量（`APFloat`可以保存任意精度的浮点数）。上面这段代码简单地创建并返回一个`ConstantFP`类的变量。注意在LLVM IR中，constants are all uniqued together and shared。因为这个原因，API使用“foo::get(...)”代替“new foo(..)”和“foo::Create(..)”。

<!-- In the LLVM IR, numeric constants are represented with the `ConstantFP` class, which holds the numeric value in an `APFloat` internally (`APFloat` has the capability of holding floating point constants of Arbitrary Precision). This code basically just creates and returns a `ConstantFP`. Note that in the LLVM IR that constants are all uniqued together and shared. For this reason, the API uses the “foo::get(...)” idiom instead of “new foo(..)” or “foo::Create(..)”. -->

```C++
Value *VariableExprAST::codegen() {
  // Look this variable up in the function.
  Value *V = NamedValues[Name];
  if (!V)
    LogErrorV("Unknown variable name");
  return V;
}
```

用LLVM处理变量的引用也非常简单。在Kaleidoscope的简单版本中，我们假设变量已经在某处定义，并且变量的值是可以获取的。实际上，`NamedValues` map中唯一能存放的变量是函数参数。上面的代码简单地检查了变量名是否在map中（如果不在，就会报出未知变量引用的错误），并返回变量的值。在后面的章节中，我们会在符号表中增加对[loop induction variables](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl5.html#for-loop-expression)的支持，以及[local variables](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl7.html#user-defined-local-variables)的支持。

<!--References to variables are also quite simple using LLVM. In the simple version of Kaleidoscope, we assume that the variable has already been emitted somewhere and its value is available. In practice, the only values that can be in the `NamedValues` map are function arguments. This code simply checks to see that the specified name is in the map (if not, an unknown variable is being referenced) and returns the value for it. In future chapters, we’ll add support for [loop induction variables](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl5.html#for-loop-expression) in the symbol table, and for [local variables](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl7.html#user-defined-local-variables).-->

```C++
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
    return Builder.CreateUIToFP(L, Type::getDoubleTy(TheContext),
                                "booltmp");
  default:
    return LogErrorV("invalid binary operator");
  }
}
```

从二元运算符开始，事情就比较有趣了。基本的思路是循环地生成代码，顺序是先处理左值，后处理右值，最后计算二元表达式的结果。在上面的代码中，我们做了一个简单的switch，跳转到正确的生成LLVM指令的代码处。

<!-- Binary operators start to get more interesting. The basic idea here is that we recursively emit code for the left-hand side of the expression, then the right-hand side, then we compute the result of the binary expression. In this code, we do a simple switch on the opcode to create the right LLVM instruction. -->

在上面的例子中，LLVM builder类开始展现它的能力了。IRBuilder知道当前应该在哪里查处新创建的指令，你需要做的只是判定该生成什么指令（比如说`CreateFAdd`），操作数是哪些（在上面的代码中是`L`和`R`），你也可以选择性地为生成的指令命名。

<!-- In the example above, the LLVM builder class is starting to show its value. IRBuilder knows where to insert the newly created instruction, all you have to do is specify what instruction to create (e.g. with `CreateFAdd`), which operands to use (`L` and `R` here) and optionally provide a name for the generated instruction. -->

LLVM有一个很好的特点是，名字只是一个指示。比如说，如果上面的代码生成了多个“addtmp”变量，LLVM可以自动地设置每次加一的后缀数字，保证命名的唯一性。指令的局部value命名真的是可选的，但是它可以让阅读IR dumps更容易。

<!-- One nice thing about LLVM is that the name is just a hint. For instance, if the code above emits multiple “addtmp” variables, LLVM will automatically provide each one with an increasing, unique numeric suffix. Local value names for instructions are purely optional, but it makes it much easier to read the IR dumps. -->

[LLVM instructions](https://releases.llvm.org/5.0.0/docs/LangRef.html#instruction-reference)的格式很严格：比如说，[add instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#add-instruction)两侧的操作数类型必须一样，加法的结果的类型过必须和操作类型匹配。因为Kaleidoscope中所有的值都是double型，使得加法、减法和乘法的代码非常简单。

<!-- [LLVM instructions](https://releases.llvm.org/5.0.0/docs/LangRef.html#instruction-reference) are constrained by strict rules: for example, the Left and Right operators of an [add instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#add-instruction) must have the same type, and the result type of the add must match the operand types. Because all values in Kaleidoscope are doubles, this makes for very simple code for add, sub and mul. -->

另一方面，LLVM可以识别[fcmp instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#fcmp-instruction)，并返回一个‘i1’类型的值（一种只有1个bit的整数）。问题是Kaleidoscope只有double型，它想要这个值是0.0或者1.0。为此，我们将fcmp instruction和[uitofp instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#uitofp-to-instruction)结合起来。这个指令将输入的整数视为无符号值，并转换成为浮点数。对比之下，如果我们用[sitofp instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#sitofp-to-instruction)，Kaleidoscope的‘<’运算符将会根据输入返回0.0或者-1.0。

<!-- On the other hand, LLVM specifies that the [fcmp instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#fcmp-instruction) always returns an ‘i1’ value (a one bit integer). The problem with this is that Kaleidoscope wants the value to be a 0.0 or 1.0 value. In order to get these semantics, we combine the fcmp instruction with a [uitofp instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#uitofp-to-instruction). This instruction converts its input integer into a floating point value by treating the input as an unsigned value. In contrast, if we used the [sitofp instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#sitofp-to-instruction), the Kaleidoscope ‘<’ operator would return 0.0 and -1.0, depending on the input value. -->

```C++
Value *CallExprAST::codegen() {
  // Look up the name in the global module table.
  Function *CalleeF = TheModule->getFunction(Callee);
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
```

LLVM中，函数调用的代码生成也非常直观。上面的代码首先在LLVM Modules的符号表中查找函数名。之前提到过，LLVM Module是在即使编译的过程中，保存函数的容器。By giving each function the same name as what the user specifies, we can use the LLVM symbol table to resolve function names for us.

<!-- Code generation for function calls is quite straightforward with LLVM. The code above initially does a function name lookup in the LLVM Module’s symbol table. Recall that the LLVM Module is the container that holds the functions we are JIT’ing. By giving each function the same name as what the user specifies, we can use the LLVM symbol table to resolve function names for us. -->

有了可以处理函数调用的方法以后，我们就可以循环地生成需要传递的每个参数，并且创建一个LLVM [call instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#call-instruction)。注意，默认情况下，LLVM使用本地C语言的函数调用规范，允许这些函数调用同时调用标准库的函数，比如“sin”、“cos”，而且不需要额外的工作。

<!-- Once we have the function to call, we recursively codegen each argument that is to be passed in, and create an LLVM [call instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#call-instruction). Note that LLVM uses the native C calling conventions by default, allowing these calls to also call into standard library functions like “sin” and “cos”, with no additional effort. -->

上面的代码封装了我们至今为止在Kaleidoscope定义的四种基本表达式。你可以增加更多类型的表达式。比如说，你可以浏览[LLVM language reference](https://releases.llvm.org/5.0.0/docs/LangRef.html)，你会发现有很多有趣的指令，它们可以非常简单地添加到我们的基础框架中。

<!-- This wraps up our handling of the four basic expressions that we have so far in Kaleidoscope. Feel free to go in and add some more. For example, by browsing the [LLVM language reference](https://releases.llvm.org/5.0.0/docs/LangRef.html) you’ll find several other interesting instructions that are really easy to plug into our basic framework. -->

## 3.4. Function Code Generation

函数原型和函数体的代码生成必须处理很多细节问题，这会让处理函数的代码不如处理表达式的代码优雅，但是可以让我们说明很多重要的点。首先，我们讨论函数原型代码生成：它们用在函数体和外部函数声明上。代码的开头部分如下：

<!-- Code generation for prototypes and functions must handle a number of details, which make their code less beautiful than expression code generation, but allows us to illustrate some important points. First, lets talk about code generation for prototypes: they are used both for function bodies and external function declarations. The code starts with: -->

```C++
Function *PrototypeAST::codegen() {
  // Make the function type:  double(double,double) etc.
  std::vector<Type*> Doubles(Args.size(),
                             Type::getDoubleTy(TheContext));
  FunctionType *FT =
    FunctionType::get(Type::getDoubleTy(TheContext), Doubles, false);

  Function *F =
    Function::Create(FT, Function::ExternalLinkage, Name, TheModule);
```

上面的代码虽然只有几行，但实际上处理了很多事情。首先，注意上面这个函数的返回值类型是“Function\*”，而不是“Value\*”。因为一个“函数原型”讨论的是一个函数的外部接口（而不是一个表达式计算出来的值），所以在生成代码时，返回它对应的LLVM Function是有意义的。

<!-- This code packs a lot of power into a few lines. Note first that this function returns a “Function\*” instead of a “Value\*”. Because a “prototype” really talks about the external interface for a function (not the value computed by an expression), it makes sense for it to return the LLVM Function it corresponds to when codegen’d. -->

对`FunctionType::get`的调用创建了应该在给定的函数原型中用到的`FunctionType`。因为Kaleidoscope中所有的函数参数都是double型的，上面函数体内第一行代码创建了一个长度为“N”的LLVM double型的vector。然后使用`Functiontype::get`方法创建了一个function type，它接受“N”个double型变量为参数，并返回一个double型变量，

The call to `FunctionType::get` creates the `FunctionType` that should be used for a given Prototype. Since all function arguments in Kaleidoscope are of type double, the first line creates a vector of “N” LLVM double types. It then uses the `Functiontype::get` method to create a function type that takes “N” doubles as arguments, returns one double as a result, and that is not vararg (the false parameter indicates this). Note that Types in LLVM are uniqued just like Constants are, so you don’t “new” a type, you “get” it.

上面的最后一行代码创建了函数原型对应的实际的IR Function。这表示type、linkage、使用的名字、以及在哪个module中插入代码。“[external linkage](https://releases.llvm.org/5.0.0/docs/LangRef.html#linkage)”意味着这个函数可能在当前module外定义，或者在当前module外可以被调用。

The final line above actually creates the IR Function corresponding to the Prototype. This indicates the type, linkage and name to use, as well as which module to insert into. “[external linkage](https://releases.llvm.org/5.0.0/docs/LangRef.html#linkage)” means that the function may be defined outside the current module and/or that it is callable by functions outside the module. The Name passed in is the name the user specified: since “`TheModule`” is specified, this name is registered in “`TheModule`“s symbol table.

```C++
// Set names for all arguments.
unsigned Idx = 0;
for (auto &Arg : F->args())
  Arg.setName(Args[Idx++]);

return F;
```

最后，我们按照函数原型中的名字为每个函数参数命名。这一步严格来说不是必须的，但是保持命名一致可以提高IR的可读性，并且让后面的代码可以直接通过参数的名字来引用它们，而不用在函数原型的AST中搜索它们。

<!-- Finally, we set the name of each of the function’s arguments according to the names given in the Prototype. This step isn’t strictly necessary, but keeping the names consistent makes the IR more readable, and allows subsequent code to refer directly to the arguments for their names, rather than having to look up them up in the Prototype AST. -->

现在我们有了不包含函数体的函数原型。这就是LLVM IR表示函数定义的方法。对Kaleidoscope中的extern语句来说，这就是我们需要做的全部了。然而对于函数定义来说，我们需要codegen，并且连接上一个函数体。

<!-- At this point we have a function prototype with no body. This is how LLVM IR represents function declarations. For extern statements in Kaleidoscope, this is as far as we need to go. For function definitions however, we need to codegen and attach a function body. -->

```C++
Function *FunctionAST::codegen() {
    // First, check for an existing function from a previous 'extern' declaration.
  Function *TheFunction = TheModule->getFunction(Proto->getName());

  if (!TheFunction)
    TheFunction = Proto->codegen();

  if (!TheFunction)
    return nullptr;

  if (!TheFunction->empty())
    return (Function*)LogErrorV("Function cannot be redefined.");
```

对函数定义来说，我们首先在TheModule的symbol table中查找这个函数，以防这个函数已经用‘extern’语句创建过了。如果Module::getFunction返回一个null，表明这个函数没有previous version，那么我们就可以从函数原型中codegen处一个。在各种情况下，如果函数是empty（也就是说，至今为止没有函数体），我们会在开始前assert。

<!-- For function definitions, we start by searching TheModule’s symbol table for an existing version of this function, in case one has already been created using an ‘extern’ statement. If Module::getFunction returns null then no previous version exists, so we’ll codegen one from the Prototype. In either case, we want to assert that the function is empty (i.e. has no body yet) before we start. -->

```C++
// Create a new basic block to start insertion into.
BasicBlock *BB = BasicBlock::Create(TheContext, "entry", TheFunction);
Builder.SetInsertPoint(BB);

// Record the function arguments in the NamedValues map.
NamedValues.clear();
for (auto &Arg : TheFunction->args())
  NamedValues[Arg.getName()] = &Arg;
```

现在`Builder`已经设置好了。上面代码的第一行创建了一个新的[basic block](http://en.wikipedia.org/wiki/Basic_block)（名为“entry”），插入在`TheFunction`中。第二行告诉builder新的指令应该插入在新的basic block后面。LLVM中的basic blocks是函数中很重要的组成部分，定义了[Control Flow Graph](http://en.wikipedia.org/wiki/Control_flow_graph)。因为我们没有任何控制流，我们的函数当前只有一个block。我们将会在[Chapter 5](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl05.html)进行增补。

<!-- Now we get to the point where the `Builder` is set up. The first line creates a new [basic block](http://en.wikipedia.org/wiki/Basic_block) (named “entry”), which is inserted into `TheFunction`. The second line then tells the builder that new instructions should be inserted into the end of the new basic block. Basic blocks in LLVM are an important part of functions that define the [Control Flow Graph](http://en.wikipedia.org/wiki/Control_flow_graph). Since we don’t have any control flow, our functions will only contain one block at this point. We’ll fix this in [Chapter 5](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl05.html) :). -->

然后，我们在NamedValues map（在首次将它清空之后）中添加了函数参数，让它们可以连接到`VariableExprAST`节点。

<!-- Next we add the function arguments to the NamedValues map (after first clearing it out) so that they’re accessible to `VariableExprAST` nodes. -->

```C++
if (Value *RetVal = Body->codegen()) {
  // Finish off the function.
  Builder.CreateRet(RetVal);

  // Validate the generated code, checking for consistency.
  verifyFunction(*TheFunction);

  return TheFunction;
}
```

设置好插入点，填充完NamedValues map后，我们为函数体的第一个表达式调用`codegen()`方法。如果没有错误，它会生成计算这个表达式的代码，插入到entry block，并且返回它计算得到的表达式的值。假设没有错误发生，我们接下来创建一条LLVM [ret instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#ret-instruction)，它会完成函数的构造。函数构造完成后，我们调用LLVM提供的`verifyFunction`，它会对生成的代码进行一系列的一致性检查，来验证我们的编译器每件事都做得正确。使用`verifyFunction`是很重要的：它能捕获很多bugs。当函数构造完成并且验证完成后，我们将它返回。

<!-- Once the insertion point has been set up and the NamedValues map populated, we call the `codegen()` method for the root expression of the function. If no error happens, this emits code to compute the expression into the entry block and returns the value that was computed. Assuming no error, we then create an LLVM [ret instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#ret-instruction), which completes the function. Once the function is built, we call `verifyFunction`, which is provided by LLVM. This function does a variety of consistency checks on the generated code, to determine if our compiler is doing everything right. Using this is important: it can catch a lot of bugs. Once the function is finished and validated, we return it. -->

```C++
  // Error reading body, remove function.
  TheFunction->eraseFromParent();
  return nullptr;
}
```

现在剩下的部分就是处理错误了。简单起见，当出错时，我们简单地调用`eraseFromParent`方法将函数删除。这让用户可以重新定义他们之前输入错误的函数：如果我们没有删除那个函数，那个函数仍然会在symbol table中，它有函数体，所以会阻止重定义。

<!-- The only piece left here is handling of the error case. For simplicity, we handle this by merely deleting the function we produced with the `eraseFromParent` method. This allows the user to redefine a function that they incorrectly typed in before: if we didn’t delete it, it would live in the symbol table, with a body, preventing future redefinition. -->

上面的代码有一个bug：如果`FunctionAST::codegen()`方法找到一个已经存在的IR Function，它并不验证函数签名和函数定义的prototype是否相同。这意味着更早的‘extern’定义比函数定义的signature有更高的优先级，这可能导致codegen失败，（比如当函数参数命名不一致时）。有几种方法去修复这个bug，这需要你自己动脑去想。下面是一个测试用例：

<!-- This code does have a bug, though: If the `FunctionAST::codegen()` method finds an existing IR Function, it does not validate its signature against the definition’s own prototype. This means that an earlier ‘extern’ declaration will take precedence over the function definition’s signature, which can cause codegen to fail, for instance if the function arguments are named differently. There are a number of ways to fix this bug, see what you can come up with! Here is a testcase: -->

```C++
extern foo(a);     # ok, defines foo.
def foo(b) b;      # Error: Unknown variable name. (decl using 'a' takes precedence).
```

## 3.5. Driver Changes and Closing Thoughts

至今为止，code generation to LLVM doesn’t really get us much，除了能看到优雅的IR调用。调用codegen将样例代码插入“`HandleDefinition`”、“`HandleExtern`”等函数，然后dumps out LLVM IR。这提供了一个查看简单函数的LLVM IR的很好的途径。举例来说：

<!-- For now, code generation to LLVM doesn’t really get us much, except that we can look at the pretty IR calls. The sample code inserts calls to codegen into the “`HandleDefinition`”, “`HandleExtern`” etc functions, and then dumps out the LLVM IR. This gives a nice way to look at the LLVM IR for simple functions. For example: -->

```bash
ready> 4+5;
Read top-level expression:
define double @0() {
entry:
  ret double 9.000000e+00
}
```

注意语法分析器是如何将顶层表达式为我们转换成匿名函数的。这一特性在下一章我们增加[JIT support](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl4.html#adding-a-jit-compiler)时非常好用。同时，注意代码基本是直接翻译过来的，没有怎么优化，除了IRBuilder做的简单的constant folding。我们将会在下一章明确地[add optimizations](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl4.html#trivial-constant-folding)。

<!-- Note how the parser turns the top-level expression into anonymous functions for us. This will be handy when we add [JIT support](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl4.html#adding-a-jit-compiler) in the next chapter. Also note that the code is very literally transcribed, no optimizations are being performed except simple constant folding done by IRBuilder. We will [add optimizations](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl4.html#trivial-constant-folding) explicitly in the next chapter. -->

```bash
ready> def foo(a b) a*a + 2*a*b + b*b;
Read function definition:
define double @foo(double %a, double %b) {
entry:
  %multmp = fmul double %a, %a
  %multmp1 = fmul double 2.000000e+00, %a
  %multmp2 = fmul double %multmp1, %b
  %addtmp = fadd double %multmp, %multmp2
  %multmp3 = fmul double %b, %b
  %addtmp4 = fadd double %addtmp, %multmp3
  ret double %addtmp4
}
```

上面的代码展示了简单的算术运算。注意，我们使用的LLVM builder calls的指令非常相似。

<!-- This shows some simple arithmetic. Notice the striking similarity to the LLVM builder calls that we use to create the instructions. -->

```
ready> def bar(a) foo(a, 4.0) + bar(31337);
Read function definition:
define double @bar(double %a) {
entry:
  %calltmp = call double @foo(double %a, double 4.000000e+00)
  %calltmp1 = call double @bar(double 3.133700e+04)
  %addtmp = fadd double %calltmp, %calltmp1
  ret double %addtmp
}
```

上面的代码展示了函数调用。注意如果你调用这个函数的话，它会执行很长的时间。将来我们会增加条件控制流，让递归变得实际可用。

<!-- This shows some function calls. Note that this function will take a long time to execute if you call it. In the future we’ll add conditional control flow to actually make recursion useful :). -->

```
ready> extern cos(x);
Read extern:
declare double @cos(double)

ready> cos(1.234);
Read top-level expression:
define double @1() {
entry:
  %calltmp = call double @cos(double 1.234000e+00)
  ret double %calltmp
}
```

上面的代码展示了数学库中“cos”函数的extern，以及对它的一次调用。

<!-- This shows an extern for the libm “cos” function, and a call to it. -->

```
ready> ^D
; ModuleID = 'my cool jit'

define double @0() {
entry:
  %addtmp = fadd double 4.000000e+00, 5.000000e+00
  ret double %addtmp
}

define double @foo(double %a, double %b) {
entry:
  %multmp = fmul double %a, %a
  %multmp1 = fmul double 2.000000e+00, %a
  %multmp2 = fmul double %multmp1, %b
  %addtmp = fadd double %multmp, %multmp2
  %multmp3 = fmul double %b, %b
  %addtmp4 = fadd double %addtmp, %multmp3
  ret double %addtmp4
}

define double @bar(double %a) {
entry:
  %calltmp = call double @foo(double %a, double 4.000000e+00)
  %calltmp1 = call double @bar(double 3.133700e+04)
  %addtmp = fadd double %calltmp, %calltmp1
  ret double %addtmp
}

declare double @cos(double)

define double @1() {
entry:
  %calltmp = call double @cos(double 1.234000e+00)
  ret double %calltmp
}
```

当你退出当前demo（通过Linux下CTRL+D，或者Windows下CTRL+Z and ENTER，发送一个EOF信号），会dumps out生成的整个module的IR。这样你就可以看到所有的函数引用。

<!-- When you quit the current demo (by sending an EOF via CTRL+D on Linux or CTRL+Z and ENTER on Windows), it dumps out the IR for the entire module generated. Here you can see the big picture with all the functions referencing each other. -->

现在封装了Kaleidoscope教程第三章的内容。下一章，我们将介绍如何[add JIT codegen and optimizer support](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl04.html)，来让我们可以实际运行代码。

<!-- This wraps up the third chapter of the Kaleidoscope tutorial. Up next, we’ll describe how to [add JIT codegen and optimizer support](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl04.html) to this so we can actually start running code! -->

## 3.6. Full Code Listing

这里是我们样例的完整代码，用LLVM code generator强化过的代码。因为使用到了LLVM库，我们需要把它们链接进来。为了做到这一点，我们使用[llvm-config](http://llvm.org/cmds/llvm-config.html)工具去告知makefile/command line我们要用哪些参数选项。

<!-- Here is the complete code listing for our running example, enhanced with the LLVM code generator. Because this uses the LLVM libraries, we need to link them in. To do this, we use the [llvm-config](http://llvm.org/cmds/llvm-config.html) tool to inform our makefile/command line about which options to use: -->

```bash
# Compile
clang++ -g -O3 toy.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core` -o toy
# Run
./toy
```

下面是完整代码：

<!-- Here is the code: -->

```C++
#include "llvm/ADT/APFloat.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/Verifier.h"
#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <memory>
#include <string>
#include <vector>

using namespace llvm;

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

Value *LogErrorV(const char *Str) {
  LogError(Str);
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
  Function *CalleeF = TheModule->getFunction(Callee);
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
  // First, check for an existing function from a previous 'extern' declaration.
  Function *TheFunction = TheModule->getFunction(Proto->getName());

  if (!TheFunction)
    TheFunction = Proto->codegen();

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

    return TheFunction;
  }

  // Error reading body, remove function.
  TheFunction->eraseFromParent();
  return nullptr;
}

//===----------------------------------------------------------------------===//
// Top-Level parsing and JIT Driver
//===----------------------------------------------------------------------===//

static void HandleDefinition() {
  if (auto FnAST = ParseDefinition()) {
    if (auto *FnIR = FnAST->codegen()) {
      fprintf(stderr, "Read function definition:");
      FnIR->print(errs());
      fprintf(stderr, "\n");
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
    }
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}

static void HandleTopLevelExpression() {
  // Evaluate a top-level expression into an anonymous function.
  if (auto FnAST = ParseTopLevelExpr()) {
    if (auto *FnIR = FnAST->codegen()) {
      fprintf(stderr, "Read top-level expression:");
      FnIR->print(errs());
      fprintf(stderr, "\n");
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
// Main driver code.
//===----------------------------------------------------------------------===//

int main() {
  // Install standard binary operators.
  // 1 is lowest precedence.
  BinopPrecedence['<'] = 10;
  BinopPrecedence['+'] = 20;
  BinopPrecedence['-'] = 20;
  BinopPrecedence['*'] = 40; // highest.

  // Prime the first token.
  fprintf(stderr, "ready> ");
  getNextToken();

  // Make the module, which holds all the code.
  TheModule = llvm::make_unique<Module>("my cool jit", TheContext);

  // Run the main "interpreter loop" now.
  MainLoop();

  // Print out all of the generated code.
  TheModule->print(errs(), nullptr);

  return 0;
}
```


