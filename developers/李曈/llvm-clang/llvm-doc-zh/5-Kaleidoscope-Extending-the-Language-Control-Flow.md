---
title: '5. Kaleidoscope: Extending the Language: Control Flow'
date: 2018-01-12 11:12:56
tags: LLVM Tutorial
---

## 5.1. Chapter 5 Introduction

欢迎来到“[用LLVM实现一门编程语言](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)”教程第5章。第1-4章介绍了简单Kaleidoscope语言的实现，并增加了生成LLVM IR的支持，以及优化器和JIT编译器。不幸的是，正如所展现的那样，Kaleidoscope用处并不大：它除了函数调用和返回以外，没有控制流。这意味着你的代码中不能有条件分支，这严重限制了代码的能力。在这一章，我们将扩展Kaleidoscope，让它可以处理if/then/else表达式，以及简单的‘for’循环。

<!-- more -->

<!-- Welcome to Chapter 5 of the “[Implementing a language with LLVM](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)” tutorial. Parts 1-4 described the implementation of the simple Kaleidoscope language and included support for generating LLVM IR, followed by optimizations and a JIT compiler. Unfortunately, as presented, Kaleidoscope is mostly useless: it has no control flow other than call and return. This means that you can’t have conditional branches in the code, significantly limiting its power. In this episode of “build that compiler”, we’ll extend Kaleidoscope to have an if/then/else expression plus a simple ‘for’ loop. -->

## 5.2. If/Then/Else

增加Kaleidoscope对if/then/else支持非常直观。需要在词法分析器、语法分析器、AST、以及LLVM代码生成器中增加“新的”概念。这个例子非常好，因为它展示了“扩展”一门语言是多么的方便，可以随着新idea的诞生不断去扩展语言的能力。

<!-- Extending Kaleidoscope to support if/then/else is quite straightforward. It basically requires adding support for this “new” concept to the lexer, parser, AST, and LLVM code emitter. This example is nice, because it shows how easy it is to “grow” a language over time, incrementally extending it as new ideas are discovered. -->

在我们开始讨论“如何”进行扩展之前，让我们先讨论一下我们想要“什么”。基本的想法是我们需要这样子的东西：

<!-- Before we get going on “how” we add this extension, lets talk about “what” we want. The basic idea is that we want to be able to write this sort of thing: -->

```
def fib(x)
  if x < 3 then
    1
  else
    fib(x-1)+fib(x-2);
```

在Kaleidoscope中，所有构造都是表达式：也就是说没有语句。这样一来，if/then/else表达式需要和其他表达式一样返回一个值。因为我们大多数用的是函数的形式，我们将计算条件式，然后根据条件式的结果返回‘then’或者‘else’值。这和C语言的”?:”表达式很相似。

<!-- In Kaleidoscope, every construct is an expression: there are no statements. As such, the if/then/else expression needs to return a value like any other. Since we’re using a mostly functional form, we’ll have it evaluate its conditional, then return the ‘then’ or ‘else’ value based on how the condition was resolved. This is very similar to the C ”?:” expression. -->

if/then/else表达式的语义是计算条件式，得到一个和boolean类型等价的值：0.0认为false，其他的值认为是true。如果条件为真，计算并返回第一个子表达式，如果条件为假，计算并返回第二个子表达式。因为Kaleidoscope允许副作用（side-effects），这个行为需要固定下来。

<!-- The semantics of the if/then/else expression is that it evaluates the condition to a boolean equality value: 0.0 is considered to be false and everything else is considered to be true. If the condition is true, the first subexpression is evaluated and returned, if the condition is false, the second subexpression is evaluated and returned. Since Kaleidoscope allows side-effects, this behavior is important to nail down. -->

现在，我们知道了我们想要”什么“，让我们分成几部分来继续深入探讨。

<!-- Now that we know what we “want”, lets break this down into its constituent pieces. -->

### 5.2.1. Lexer Extensions for If/Then/Else

词法分析器的扩展很直观。首先，我们为相关的token增加enum值。

<!-- The lexer extensions are straightforward. First we add new enum values for the relevant tokens: -->

```C++
// control
tok_if = -6,
tok_then = -7,
tok_else = -8,
```

有了这个以后，我们就可以在词法分析器中识别新的关键字（keyword）。接下来就是很平常的工作：

<!-- Once we have that, we recognize the new keywords in the lexer. This is pretty simple stuff: -->

```C++
...
if (IdentifierStr == "def")
  return tok_def;
if (IdentifierStr == "extern")
  return tok_extern;
if (IdentifierStr == "if")
  return tok_if;
if (IdentifierStr == "then")
  return tok_then;
if (IdentifierStr == "else")
  return tok_else;
return tok_identifier;
```

### 5.2.2. AST Extensions for If/Then/Else

为了表示新的表达式，我们为它增加了新的AST节点：

<!-- To represent the new expression we add a new AST node for it: -->

```C++
/// IfExprAST - Expression class for if/then/else.
class IfExprAST : public ExprAST {
  std::unique_ptr<ExprAST> Cond, Then, Else;

public:
  IfExprAST(std::unique_ptr<ExprAST> Cond, std::unique_ptr<ExprAST> Then,
            std::unique_ptr<ExprAST> Else)
    : Cond(std::move(Cond)), Then(std::move(Then)), Else(std::move(Else)) {}

  Value *codegen() override;
};
```

这个AST节点只包含了指向不同子表达式的指针。

<!-- The AST node just has pointers to the various subexpressions. -->

### 5.2.3. Parser Extensions for If/Then/Else

现在我们在词法分析器中有了相关的tokens，也有了相关的AST节点，我们的语法分析逻辑就很直观了。首先定义一个新的语法分析函数：

<!-- Now that we have the relevant tokens coming from the lexer and we have the AST node to build, our parsing logic is relatively straightforward. First we define a new parsing function: -->

```C++
/// ifexpr ::= 'if' expression 'then' expression 'else' expression
static std::unique_ptr<ExprAST> ParseIfExpr() {
  getNextToken();  // eat the if.

  // condition.
  auto Cond = ParseExpression();
  if (!Cond)
    return nullptr;

  if (CurTok != tok_then)
    return LogError("expected then");
  getNextToken();  // eat the then

  auto Then = ParseExpression();
  if (!Then)
    return nullptr;

  if (CurTok != tok_else)
    return LogError("expected else");

  getNextToken();

  auto Else = ParseExpression();
  if (!Else)
    return nullptr;

  return llvm::make_unique<IfExprAST>(std::move(Cond), std::move(Then),
                                      std::move(Else));
}
```

接下来，我们将它作为一个primary表达式，添加一个钩子。

<!-- Next we hook it up as a primary expression: -->

```C++
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
  case tok_if:
    return ParseIfExpr();
  }
}
```

### 5.2.4. LLVM IR for If/Then/Else

现在我们完成了if/then/else的语法分析，并构造了相应的AST，最后一步就是增加LLVM代码生成的支持了。这是if/then/else例子中最有意思的一部分，因为从这里开始将会引入新的概念。上面的代码在之前的章节里都已经详细地描述过了。

<!-- Now that we have it parsing and building the AST, the final piece is adding LLVM code generation support. This is the most interesting part of the if/then/else example, because this is where it starts to introduce new concepts. All of the code above has been thoroughly described in previous chapters. -->

为了调用大家的积极性，让我们先预览一个简单的例子：

<!-- To motivate the code we want to produce, lets take a look at a simple example. Consider: -->

```
extern foo();
extern bar();
def baz(x) if x then foo() else bar();
```

如果不做任何优化，你得到的代码将是这个样子的：

<!-- If you disable optimizations, the code you’ll (soon) get from Kaleidoscope looks like this: -->

```
declare double @foo()

declare double @bar()

define double @baz(double %x) {
entry:
  %ifcond = fcmp one double %x, 0.000000e+00
  br i1 %ifcond, label %then, label %else

then:       ; preds = %entry
  %calltmp = call double @foo()
  br label %ifcont

else:       ; preds = %entry
  %calltmp1 = call double @bar()
  br label %ifcont

ifcont:     ; preds = %else, %then
  %iftmp = phi double [ %calltmp, %then ], [ %calltmp1, %else ]
  ret double %iftmp
}
```

如果想看直观的控制流图，你可以使用LLVM的一个很有用的工具：‘[opt](http://llvm.org/cmds/opt.html)‘ tool。将这些LLVM IR保存到“t.ll”文件中，执行“`llvm-as < t.ll | opt -analyze -view-cfg`”命令，[将会弹出一个窗口](https://releases.llvm.org/5.0.0/docs/ProgrammersManual.html#viewing-graphs-while-debugging-code)，你将会看到这幅图：

<!-- To visualize the control flow graph, you can use a nifty feature of the LLVM ‘[opt](http://llvm.org/cmds/opt.html)‘ tool. If you put this LLVM IR into “t.ll” and run “`llvm-as < t.ll | opt -analyze -view-cfg`”, [a window will pop up](https://releases.llvm.org/5.0.0/docs/ProgrammersManual.html#viewing-graphs-while-debugging-code) and you’ll see this graph: -->

![Example CFG](http://oy60g0sqx.bkt.clouddn.com/2018-01-10-LangImpl05-cfg.png)

获取这幅图的另一个方法是调用“`F->viewCFG()`”或者“`F->viewCFGOnly()`”（这里的F是一个函数指针“`Function*`”）中的一个，插入到代码中并重新编译，或者在debugger中调用它们。LLVM有很多很好的特性，可以将不同的图可视化。

<!-- Another way to get this is to call “`F->viewCFG()`” or “`F->viewCFGOnly()`” (where F is a “`Function*`”) either by inserting actual calls into the code and recompiling or by calling these in the debugger. LLVM has many nice features for visualizing various graphs. -->

再回到生成的代码，代码是比较简单的：entry block计算条件表达式（在这个例子中是“x”），用“`fcmp one`”指令将计算的结果和0.0比较（‘one’表示“Ordered and Not Equal”）。基于这个表达式的计算结果，代码将跳转到包含了true/false情况下要计算的表达式的“then”或者“else” bolcks。

<!-- Getting back to the generated code, it is fairly simple: the entry block evaluates the conditional expression (“x” in our case here) and compares the result to 0.0 with the “`fcmp one`” instruction (‘one’ is “Ordered and Not Equal”). Based on the result of this expression, the code jumps to either the “then” or “else” blocks, which contain the expressions for the true/false cases. -->

当then/else blocks执行完后，它们都会跳回到‘ifcont’ block，去执行if/then/else之后的代码。在这种情况下，剩下的唯一一件事就是返回到这个函数的调用者。那么问题来了：代码如何知道该返回那个表达式呢？

<!-- Once the then/else blocks are finished executing, they both branch back to the ‘ifcont’ block to execute the code that happens after the if/then/else. In this case the only thing left to do is to return to the caller of the function. The question then becomes: how does the code know which expression to return? -->

这个问题的答案需要一个重要的SSA操作符：[Phi operation](http://en.wikipedia.org/wiki/Static_single_assignment_form)。如果你对SSA不熟悉，[the wikipedia article](http://en.wikipedia.org/wiki/Static_single_assignment_form)是一篇很好的介绍，你还可以在搜索引擎上搜索更多资料。简单来说，Phi operation的“执行”需要“记住”控制流来自哪里。Phi operation会记录输入控制流对应的值。在这种情况下，如果控制流来自于“then”block，它就会获得“calltmp”的值。如果控制流来自于“else”block，他就会获得“calltmp1”的值。

<!-- The answer to this question involves an important SSA operation: the [Phi operation](http://en.wikipedia.org/wiki/Static_single_assignment_form). If you’re not familiar with SSA, [the wikipedia article](http://en.wikipedia.org/wiki/Static_single_assignment_form) is a good introduction and there are various other introductions to it available on your favorite search engine. The short version is that “execution” of the Phi operation requires “remembering” which block control came from. The Phi operation takes on the value corresponding to the input control block. In this case, if control comes in from the “then” block, it gets the value of “calltmp”. If control comes from the “else” block, it gets the value of “calltmp1”. -->

现在，你可能会想“Oh no！这意味着我简单而优雅的前端将为了使用LLVM而开始生成SSA了！”幸运的是，事情并不是这样的，我们非常不推荐你在前端中实现一个SSA构造算法，除非你有非常充分的理由这么做。实际上，there are two sorts of values that float around in code written for your average imperative programming language that might need Phi nodes:

<!-- At this point, you are probably starting to think “Oh no! This means my simple and elegant front-end will have to start generating SSA form in order to use LLVM!”. Fortunately, this is not the case, and we strongly advise not implementing an SSA construction algorithm in your front-end unless there is an amazingly good reason to do so. In practice, there are two sorts of values that float around in code written for your average imperative programming language that might need Phi nodes: -->

1. 包含用户变量的代码：`x = 1; x = x + 1`；
2. 隐含在你的AST结构中的值，比如这里的Phi节点。

<!-- 1. Code that involves user variables: `x = 1; x = x + 1`;
2. Values that are implicit in the structure of your AST, such as the Phi node in this case. -->

在教程的[第7章](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl07.html)，我们更深入地讨论#1。现在，请相信我，为了解决现在的问题，你不需要构造SSA。对于#2，你可以选择使用我们将会在#1介绍的技术，或者方便的话，你可以直接插入Phi节点。在这种情况下，生成Phi节点真的很方便，所以我们选择直接插入Phi节点。

<!-- In [Chapter 7](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl07.html) of this tutorial (“mutable variables”), we’ll talk about #1 in depth. For now, just believe me that you don’t need SSA construction to handle this case. For #2, you have the choice of using the techniques that we will describe for #1, or you can insert Phi nodes directly, if convenient. In this case, it is really easy to generate the Phi node, so we choose to do it directly. -->

Okay，现在有了足够的动力和预览了，让我们开始生成代码！

<!-- Okay, enough of the motivation and overview, lets generate code! -->

### 5.2.5. Code Generation for If/Then/Else

为了生成代码，我们为`IfExprAST`实现了`codegen`方法：

<!-- In order to generate code for this, we implement the `codegen` method for `IfExprAST`: -->

```C++
Value *IfExprAST::codegen() {
  Value *CondV = Cond->codegen();
  if (!CondV)
    return nullptr;

  // Convert condition to a bool by comparing non-equal to 0.0.
  CondV = Builder.CreateFCmpONE(
      CondV, ConstantFP::get(TheContext, APFloat(0.0)), "ifcond");
```

上面的代码非常直观，和我们之前见到的也很相似。我们生成了if条件的表达式，然后计算它的值并和0比较，从而获得一个1 bit（bool）的值作为真正的value。

<!-- This code is straightforward and similar to what we saw before. We emit the expression for the condition, then compare that value to zero to get a truth value as a 1-bit (bool) value. -->

```C++
Function *TheFunction = Builder.GetInsertBlock()->getParent();

// Create blocks for the then and else cases.  Insert the 'then' block at the
// end of the function.
BasicBlock *ThenBB = BasicBlock::Create(TheContext, "then", TheFunction);
BasicBlock *ElseBB = BasicBlock::Create(TheContext, "else");
BasicBlock *MergeBB = BasicBlock::Create(TheContext, "ifcont");

Builder.CreateCondBr(CondV, ThenBB, ElseBB);
```

上面的代码创建了basic blocks，并关联到if/then/else语句，和上面的例子命名一一对应。代码的第一行获取正在build的函数对象，方法是获取询问当前BasicBlock的builder，然后获取它的“parent” block（也就是当前block嵌入的函数）。

<!-- This code creates the basic blocks that are related to the if/then/else statement, and correspond directly to the blocks in the example above. The first line gets the current Function object that is being built. It gets this by asking the builder for the current BasicBlock, and asking that block for its “parent” (the function it is currently embedded into). -->

有了函数对象以后，创建了三个blocks。注意在“then” block的构造器中传递了“TheFunction”。这导致构造器将新的blockk自动插入到该函数的末尾。另外两个block创建后，但至今没有插入到函数中。

<!-- Once it has that, it creates three blocks. Note that it passes “TheFunction” into the constructor for the “then” block. This causes the constructor to automatically insert the new block into the end of the specified function. The other two blocks are created, but aren’t yet inserted into the function. -->

当blocks创建后，我们可以生成用来选择哪条block执行的条件分支。注意创建新的blocks并不会影响IRBuilder，所以它仍然会把代码插入condition进入的block。同时注意，CondV和“then” block、“else” block建立了branch，即时“else” block至今没有插入到函数中。这是ok的，这是一种标准的处理方式，LLVM支持forward references。

<!-- Once the blocks are created, we can emit the conditional branch that chooses between them. Note that creating new blocks does not implicitly affect the IRBuilder, so it is still inserting into the block that the condition went into. Also note that it is creating a branch to the “then” block and the “else” block, even though the “else” block isn’t inserted into the function yet. This is all ok: it is the standard way that LLVM supports forward references. -->

```C++
// Emit then value.
Builder.SetInsertPoint(ThenBB);

Value *ThenV = Then->codegen();
if (!ThenV)
  return nullptr;

Builder.CreateBr(MergeBB);
// Codegen of 'Then' can change the current block, update ThenBB for the PHI.
ThenBB = Builder.GetInsertBlock();
```

条件分支插入后，我们移动builder，开始在“then” block插入代码。严格来说，这个调用会将插入点移动到该block的末尾。然而，“then” block目前是空的，那么也就相当于在block开头插入了。

<!-- After the conditional branch is inserted, we move the builder to start inserting into the “then” block. Strictly speaking, this call moves the insertion point to be at the end of the specified block. However, since the “then” block is empty, it also starts out by inserting at the beginning of the block. :) -->

当插入点设置好后，我们从AST上递归的codegen “then”表达式。为了结束“then” block，我们创建一条非条件分支到merge block。LLVM IR的一个有趣的（并且非常重要的）点是它[requires all basic blocks to be “terminated”](https://releases.llvm.org/5.0.0/docs/LangRef.html#functionstructure) with a [control flow instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#terminators) such as return or branch。这意味着所有的控制流，包括fall throughs，在LLVM IR中必须是显式的。如果你违反了这条规则，verifier会报错。

<!-- Once the insertion point is set, we recursively codegen the “then” expression from the AST. To finish off the “then” block, we create an unconditional branch to the merge block. One interesting (and very important) aspect of the LLVM IR is that it [requires all basic blocks to be “terminated”](https://releases.llvm.org/5.0.0/docs/LangRef.html#functionstructure) with a [control flow instruction](https://releases.llvm.org/5.0.0/docs/LangRef.html#terminators) such as return or branch. This means that all control flow, including fall throughs must be made explicit in the LLVM IR. If you violate this rule, the verifier will emit an error. -->

最后一行代码比较微妙，但很重要。基本的问题是当我们在merge block中创建了Phi节点后，我们需要设置block/value pairs去指导Phi如何工作。重要的是，the Phi node expects to have an entry for each predecessor of the block in the CFG。那么我们为什么要在5行代码之前将当前block设置到ThenBB呢？问题在于“Then”表达式

The final line here is quite subtle, but is very important. The basic issue is that when we create the Phi node in the merge block, we need to set up the block/value pairs that indicate how the Phi will work. Importantly, the Phi node expects to have an entry for each predecessor of the block in the CFG. Why then, are we getting the current block when we just set it to ThenBB 5 lines above? The problem is that the “Then” expression may actually itself change the block that the Builder is emitting into if, for example, it contains a nested “if/then/else” expression. Because calling `codegen()` recursively could arbitrarily change the notion of the current block, we are required to get an up-to-date value for code that will set up the Phi node.

```C++
// Emit else block.
TheFunction->getBasicBlockList().push_back(ElseBB);
Builder.SetInsertPoint(ElseBB);

Value *ElseV = Else->codegen();
if (!ElseV)
  return nullptr;

Builder.CreateBr(MergeBB);
// codegen of 'Else' can change the current block, update ElseBB for the PHI.
ElseBB = Builder.GetInsertBlock();
```

‘else’ block的代码生成和‘then’ block基本是一样的。唯一重要的区别在于第一行代码，将‘else’ block添加到函数中了。之前创建‘else’ block的时候，并没有添加到函数中。现在‘then’和‘else’ block都生成好了，我们可以用merge code结尾了。

<!-- Code generation for the ‘else’ block is basically identical to codegen for the ‘then’ block. The only significant difference is the first line, which adds the ‘else’ block to the function. Recall previously that the ‘else’ block was created, but not added to the function. Now that the ‘then’ and ‘else’ blocks are emitted, we can finish up with the merge code: -->

```C++
  // Emit merge block.
  TheFunction->getBasicBlockList().push_back(MergeBB);
  Builder.SetInsertPoint(MergeBB);
  PHINode *PN =
    Builder.CreatePHI(Type::getDoubleTy(TheContext), 2, "iftmp");

  PN->addIncoming(ThenV, ThenBB);
  PN->addIncoming(ElseV, ElseBB);
  return PN;
}
```

前两行代码很眼熟：第一行将“merge” block添加到函数对象中（这个block之前和上面的else block一样是漂浮着的）。第二行改变了插入点，让新生成的代码插入到“merge” block中。这些完成后，我们需要创建PHI节点，并为它设置block/value pairs。

<!-- The first two lines here are now familiar: the first adds the “merge” block to the Function object (it was previously floating, like the else block above). The second changes the insertion point so that newly created code will go into the “merge” block. Once that is done, we need to create the PHI node and set up the block/value pairs for the PHI. -->

最后，CodeGen函数返回phi节点作为if/then/else表达式的计算结果。在上面的例子中，返回的值将feed into the code for the top-level function, which will create the return instruction。

<!-- Finally, the CodeGen function returns the phi node as the value computed by the if/then/else expression. In our example above, this returned value will feed into the code for the top-level function, which will create the return instruction. -->

小结一下，我们现在可以在Kaleidoscope中执行条件代码了。随着这个扩展，Kaleidoscope就成为相对完整的语言了，可以执行很多数值计算的函数。下一步我们将增加另一个非常有用的表达式，在非函数式编程语言中非常常见。

<!-- Overall, we now have the ability to execute conditional code in Kaleidoscope. With this extension, Kaleidoscope is a fairly complete language that can calculate a wide variety of numeric functions. Next up we’ll add another useful expression that is familiar from non-functional languages... -->

## 5.3. ‘for’ Loop Expression

现在我们知道如何为语言添加基本的控制流结构了，我们有足够的工具，可以增加更多有力的语句。让我们增加一个更有挑战的，‘for’表达式：

<!-- Now that we know how to add basic control flow constructs to the language, we have the tools to add more powerful things. Lets add something more aggressive, a ‘for’ expression: -->

```
extern putchard(char);
def printstar(n)
  for i = 1, i < n, 1.0 in
    putchard(42);  # ascii 42 = '*'

# print 100 '*' characters
printstar(100);
```

这个表达式定义了一个新变量（在这里是“i”），它从初始值开始迭代，当条件（在这里是“i<n”）为真时，该变量自增一个任意设置的step value（在这里是“1.0”）。如果这个step value省略了，将会默认为1.0。当循环的条件为真时，就执行循环体的表达式。因为没有什么合适的值return，我们就定义循环总是返回0.0。将来等我们有了mutable变量后，循环语句将会变得更有用。

<!-- This expression defines a new variable (“i” in this case) which iterates from a starting value, while the condition (“i < n” in this case) is true, incrementing by an optional step value (“1.0” in this case). If the step value is omitted, it defaults to 1.0. While the loop is true, it executes its body expression. Because we don’t have anything better to return, we’ll just define the loop as always returning 0.0. In the future when we have mutable variables, it will get more useful. -->

开始之前，让我们先讨论一下为了让Kaleidoscope支持循环，需要做哪些改变。

<!-- As before, lets talk about the changes that we need to Kaleidoscope to support this. -->

### 5.3.1. Lexer Extensions for the ‘for’ Loop

词法分析器的扩展和if/then/else很相似：

<!-- The lexer extensions are the same sort of thing as for if/then/else: -->

```C++
... in enum Token ...
// control
tok_if = -6, tok_then = -7, tok_else = -8,
tok_for = -9, tok_in = -10

... in gettok ...
if (IdentifierStr == "def")
  return tok_def;
if (IdentifierStr == "extern")
  return tok_extern;
if (IdentifierStr == "if")
  return tok_if;
if (IdentifierStr == "then")
  return tok_then;
if (IdentifierStr == "else")
  return tok_else;
if (IdentifierStr == "for")
  return tok_for;
if (IdentifierStr == "in")
  return tok_in;
return tok_identifier;
```

### 5.3.2. AST Extensions for the ‘for’ Loop

AST节点很简单。基本可以归结为保存变量名以及节点中包含的表达式。

<!-- The AST node is just as simple. It basically boils down to capturing the variable name and the constituent expressions in the node. -->

```C++
/// ForExprAST - Expression class for for/in.
class ForExprAST : public ExprAST {
  std::string VarName;
  std::unique_ptr<ExprAST> Start, End, Step, Body;

public:
  ForExprAST(const std::string &VarName, std::unique_ptr<ExprAST> Start,
             std::unique_ptr<ExprAST> End, std::unique_ptr<ExprAST> Step,
             std::unique_ptr<ExprAST> Body)
    : VarName(VarName), Start(std::move(Start)), End(std::move(End)),
      Step(std::move(Step)), Body(std::move(Body)) {}

  Value *codegen() override;
};
```

### 5.3.3. Parser Extensions for the ‘for’ Loop

语法分析的代码比较标准化。这里唯一有趣的事情是处理可任意设置的step value。语法分析的代码通过检测第二个逗号是否存在来处理它。如果不存在，在AST节点中，step value将设置为null。

<!-- The parser code is also fairly standard. The only interesting thing here is handling of the optional step value. The parser code handles it by checking to see if the second comma is present. If not, it sets the step value to null in the AST node: -->

```C++
/// forexpr ::= 'for' identifier '=' expr ',' expr (',' expr)? 'in' expression
static std::unique_ptr<ExprAST> ParseForExpr() {
  getNextToken();  // eat the for.

  if (CurTok != tok_identifier)
    return LogError("expected identifier after for");

  std::string IdName = IdentifierStr;
  getNextToken();  // eat identifier.

  if (CurTok != '=')
    return LogError("expected '=' after for");
  getNextToken();  // eat '='.


  auto Start = ParseExpression();
  if (!Start)
    return nullptr;
  if (CurTok != ',')
    return LogError("expected ',' after for start value");
  getNextToken();

  auto End = ParseExpression();
  if (!End)
    return nullptr;

  // The step value is optional.
  std::unique_ptr<ExprAST> Step;
  if (CurTok == ',') {
    getNextToken();
    Step = ParseExpression();
    if (!Step)
      return nullptr;
  }

  if (CurTok != tok_in)
    return LogError("expected 'in' after for");
  getNextToken();  // eat 'in'.

  auto Body = ParseExpression();
  if (!Body)
    return nullptr;

  return llvm::make_unique<ForExprAST>(IdName, std::move(Start),
                                       std::move(End), std::move(Step),
                                       std::move(Body));
}
```

然后我们hook it up as a primary expression：

<!-- And again we hook it up as a primary expression: -->

```C++
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
  case tok_if:
    return ParseIfExpr();
  case tok_for:
    return ParseForExpr();
  }
}
```

### 5.3.4. LLVM IR for the ‘for’ Loop

现在我们该生成LLVM IR了。随着上面的简单的例子，我们得到如下的LLVM IR（注意，这里的dump是在没有任何优化的情况下生成的）：

<!-- Now we get to the good part: the LLVM IR we want to generate for this thing. With the simple example above, we get this LLVM IR (note that this dump is generated with optimizations disabled for clarity): -->

```
declare double @putchard(double)

define double @printstar(double %n) {
entry:
  ; initial value = 1.0 (inlined into phi)
  br label %loop

loop:       ; preds = %loop, %entry
  %i = phi double [ 1.000000e+00, %entry ], [ %nextvar, %loop ]
  ; body
  %calltmp = call double @putchard(double 4.200000e+01)
  ; increment
  %nextvar = fadd double %i, 1.000000e+00

  ; termination test
  %cmptmp = fcmp ult double %i, %n
  %booltmp = uitofp i1 %cmptmp to double
  %loopcond = fcmp one double %booltmp, 0.000000e+00
  br i1 %loopcond, label %loop, label %afterloop

afterloop:      ; preds = %loop
  ; loop always returns 0.0
  ret double 0.000000e+00
}
```

这个循环包含了我们之前看到的所有结构：一个phi节点，几个表达式，几个basic blocks。让我们看看这些东西在一起是如何工作的吧。

<!-- This loop contains all the same constructs we saw before: a phi node, several expressions, and some basic blocks. Lets see how this fits together. -->

### 5.3.5. Code Generation for the ‘for’ Loop

codegen的第一部分很简单：我们只是输出了loop value的初始表达式：

<!-- The first part of codegen is very simple: we just output the start expression for the loop value: -->

```C++
Value *ForExprAST::codegen() {
  // Emit the start code first, without 'variable' in scope.
  Value *StartVal = Start->codegen();
  if (!StartVal)
    return nullptr;
```

做好后，下一步就是设置LLVM basic block到循环体的开头处。在上面的情况中，整个循环体是一个block，但是请记住，循环体的代码可能包含多个blocks（比如说，如果循环体包含了if/then/else表达式或者for/in表达式）。

<!-- With this out of the way, the next step is to set up the LLVM basic block for the start of the loop body. In the case above, the whole loop body is one block, but remember that the body code itself could consist of multiple blocks (e.g. if it contains an if/then/else or a for/in expression). -->

```C++
// Make the new basic block for the loop header, inserting after current
// block.
Function *TheFunction = Builder.GetInsertBlock()->getParent();
BasicBlock *PreheaderBB = Builder.GetInsertBlock();
BasicBlock *LoopBB =
    BasicBlock::Create(TheContext, "loop", TheFunction);

// Insert an explicit fall through from the current block to the LoopBB.
Builder.CreateBr(LoopBB);
```

上面的代码和我们在if/then/else中看到的很像。因为我们需要用它来创建Phi节点，我们记录进入这个循环的block。当我们有了它以后，我们创建开始循环的实际block，并创建一个非条件分支for the fall-through between the two blocks。

<!-- This code is similar to what we saw for if/then/else. Because we will need it to create the Phi node, we remember the block that falls through into the loop. Once we have that, we create the actual block that starts the loop and create an unconditional branch for the fall-through between the two blocks. -->

```C++
// Start insertion in LoopBB.
Builder.SetInsertPoint(LoopBB);

// Start the PHI node with an entry for Start.
PHINode *Variable = Builder.CreatePHI(Type::getDoubleTy(TheContext),
                                      2, VarName.c_str());
Variable->addIncoming(StartVal, PreheaderBB);
```

现在循环的“preheader”已经设置好了，我们开始生成循环体的代码。首先，我们移动插入点，并为loop induction变量创建PHI节点。因为我们已经知道了即将到来的初始值，我们将它添加到Phi节点中。注意，Phi最终将为backedge获得第二个值，但我们现在不能设置它（因为它并不存在！）。

<!-- Now that the “preheader” for the loop is set up, we switch to emitting code for the loop body. To begin with, we move the insertion point and create the PHI node for the loop induction variable. Since we already know the incoming value for the starting value, we add it to the Phi node. Note that the Phi will eventually get a second value for the backedge, but we can’t set it up yet (because it doesn’t exist!). -->

```C++
// Within the loop, the variable is defined equal to the PHI node.  If it
// shadows an existing variable, we have to restore it, so save it now.
Value *OldVal = NamedValues[VarName];
NamedValues[VarName] = Variable;

// Emit the body of the loop.  This, like any other expr, can change the
// current BB.  Note that we ignore the value computed by the body, but don't
// allow an error.
if (!Body->codegen())
  return nullptr;
```

现在代码变得更有趣了。我们的‘for’循环向symbol table引入了新变量。这意味着我们的symbol table现在包含了函数参数和循环变量。为了解决它，在codegen循环体之前，我们add the loop variable as the current value for its name。注意，在外部作用域中可能存在同名变量。这很容易造成错误（如果VarName已经有entry，将会生成一个error，并返回null），但是我们选择允许shadowing of variables。为了正确处理它，我们在`OldVal`中记录可能会shadowing的值（如果没有shadowed variable的话就为空）。

<!-- Now the code starts to get more interesting. Our ‘for’ loop introduces a new variable to the symbol table. This means that our symbol table can now contain either function arguments or loop variables. To handle this, before we codegen the body of the loop, we add the loop variable as the current value for its name. Note that it is possible that there is a variable of the same name in the outer scope. It would be easy to make this an error (emit an error and return null if there is already an entry for VarName) but we choose to allow shadowing of variables. In order to handle this correctly, we remember the Value that we are potentially shadowing in `OldVal` (which will be null if there is no shadowed variable). -->

当循环变量在symbol table中设置好后，代码将会递归地codegen函数体。这允许函数体使用循环变量：任何使用循环变量的引用都会在symbol table中找到它。

<!-- Once the loop variable is set into the symbol table, the code recursively codegen’s the body. This allows the body to use the loop variable: any references to it will naturally find it in the symbol table. -->

```C++
// Emit the step value.
Value *StepVal = nullptr;
if (Step) {
  StepVal = Step->codegen();
  if (!StepVal)
    return nullptr;
} else {
  // If not specified, use 1.0.
  StepVal = ConstantFP::get(TheContext, APFloat(1.0));
}

Value *NextVar = Builder.CreateFAdd(Variable, StepVal, "nextvar");
```

注意循环体生成后，我们将把循环变量增加step value（如果没有设置的话就默认为1.0），得到下一轮迭代的值。‘`NextVar`‘将会是循环的下一次迭代中的循环变量的值。

<!-- Now that the body is emitted, we compute the next value of the iteration variable by adding the step value, or 1.0 if it isn’t present. ‘`NextVar`‘ will be the value of the loop variable on the next iteration of the loop. -->

```C++
// Compute the end condition.
Value *EndCond = End->codegen();
if (!EndCond)
  return nullptr;

// Convert condition to a bool by comparing non-equal to 0.0.
EndCond = Builder.CreateFCmpONE(
    EndCond, ConstantFP::get(TheContext, APFloat(0.0)), "loopcond");
```

最后，我们将计算循环的退出值，来决定循环什么时候结束。这部分和if/then/else语句的处理是一样的。

<!-- Finally, we evaluate the exit value of the loop, to determine whether the loop should exit. This mirrors the condition evaluation for the if/then/else statement. -->

```C++
// Create the "after loop" block and insert it.
BasicBlock *LoopEndBB = Builder.GetInsertBlock();
BasicBlock *AfterBB =
    BasicBlock::Create(TheContext, "afterloop", TheFunction);

// Insert the conditional branch into the end of LoopEndBB.
Builder.CreateCondBr(EndCond, LoopBB, AfterBB);

// Any new code will be inserted in AfterBB.
Builder.SetInsertPoint(AfterBB);
```

循环体的代码结束后，我们只需要结束它的控制流就可以了。上面的代码记录了block的结尾（为了phi节点），然后为循环结束创建了一个block（“afterloop”）。基于退出条件的值，它将创建一个条件分支来选择再一次执行循环还是退出循环。所有后续的代码都在“afterloop” block中生成，所以将插入点设置在这里。

<!-- With the code for the body of the loop complete, we just need to finish up the control flow for it. This code remembers the end block (for the phi node), then creates the block for the loop exit (“afterloop”). Based on the value of the exit condition, it creates a conditional branch that chooses between executing the loop again and exiting the loop. Any future code is emitted in the “afterloop” block, so it sets the insertion position to it. -->

```C++
  // Add a new entry to the PHI node for the backedge.
  Variable->addIncoming(NextVar, LoopEndBB);

  // Restore the unshadowed variable.
  if (OldVal)
    NamedValues[VarName] = OldVal;
  else
    NamedValues.erase(VarName);

  // for expr always returns 0.0.
  return Constant::getNullValue(Type::getDoubleTy(TheContext));
}
```

最后的代码处理不同种类的cleanup：现在我们有“NextVar”值，我们可以给循环的PHI节点添加即将到来的值。在那之后，我们将循环变量移出symbol table，所以在循环结束后，就出了作用域了。最后，循环的代码生成总是返回0.0，那就是`ForExprAST::codegen()`返回的值。

<!-- The final code handles various cleanups: now that we have the “NextVar” value, we can add the incoming value to the loop PHI node. After that, we remove the loop variable from the symbol table, so that it isn’t in scope after the for loop. Finally, code generation of the for loop always returns 0.0, so that is what we return from `ForExprAST::codegen()`. -->

这样一来，我们就完成了教程的“adding control flow to Kaleidoscope”一章。在这一章中，我们增加了两个控制流结构，并用它们介绍了LLVM IR中的一些知识，这些知识对编译器前端的实现来说是很重要的。下一章更疯狂，我们将会为我们贫瘠的编程语言添加[user-defined operators](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl06.html)。

<!-- With this, we conclude the “adding control flow to Kaleidoscope” chapter of the tutorial. In this chapter we added two control flow constructs, and used them to motivate a couple of aspects of the LLVM IR that are important for front-end implementors to know. In the next chapter of our saga, we will get a bit crazier and add [user-defined operators](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl06.html) to our poor innocent language. -->

## 5.4. Full Code Listing

这里是我们的例子的完整代码，这一章增加了if/then/else和for表达式。用下面的指令build这个例子：

<!-- Here is the complete code listing for our running example, enhanced with the if/then/else and for expressions. To build this example, use: -->

```bash
# Compile
clang++ -g toy.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core mcjit native` -O3 -o toy
# Run
./toy
```

下面是完整的代码：

<!-- Here is the code: -->

```C++
#include "llvm/ADT/APFloat.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
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
  tok_number = -5,

  // control
  tok_if = -6,
  tok_then = -7,
  tok_else = -8,
  tok_for = -9,
  tok_in = -10
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
    if (IdentifierStr == "if")
      return tok_if;
    if (IdentifierStr == "then")
      return tok_then;
    if (IdentifierStr == "else")
      return tok_else;
    if (IdentifierStr == "for")
      return tok_for;
    if (IdentifierStr == "in")
      return tok_in;
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

/// IfExprAST - Expression class for if/then/else.
class IfExprAST : public ExprAST {
  std::unique_ptr<ExprAST> Cond, Then, Else;

public:
  IfExprAST(std::unique_ptr<ExprAST> Cond, std::unique_ptr<ExprAST> Then,
            std::unique_ptr<ExprAST> Else)
      : Cond(std::move(Cond)), Then(std::move(Then)), Else(std::move(Else)) {}

  Value *codegen() override;
};

/// ForExprAST - Expression class for for/in.
class ForExprAST : public ExprAST {
  std::string VarName;
  std::unique_ptr<ExprAST> Start, End, Step, Body;

public:
  ForExprAST(const std::string &VarName, std::unique_ptr<ExprAST> Start,
             std::unique_ptr<ExprAST> End, std::unique_ptr<ExprAST> Step,
             std::unique_ptr<ExprAST> Body)
      : VarName(VarName), Start(std::move(Start)), End(std::move(End)),
        Step(std::move(Step)), Body(std::move(Body)) {}

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

/// ifexpr ::= 'if' expression 'then' expression 'else' expression
static std::unique_ptr<ExprAST> ParseIfExpr() {
  getNextToken(); // eat the if.

  // condition.
  auto Cond = ParseExpression();
  if (!Cond)
    return nullptr;

  if (CurTok != tok_then)
    return LogError("expected then");
  getNextToken(); // eat the then

  auto Then = ParseExpression();
  if (!Then)
    return nullptr;

  if (CurTok != tok_else)
    return LogError("expected else");

  getNextToken();

  auto Else = ParseExpression();
  if (!Else)
    return nullptr;

  return llvm::make_unique<IfExprAST>(std::move(Cond), std::move(Then),
                                      std::move(Else));
}

/// forexpr ::= 'for' identifier '=' expr ',' expr (',' expr)? 'in' expression
static std::unique_ptr<ExprAST> ParseForExpr() {
  getNextToken(); // eat the for.

  if (CurTok != tok_identifier)
    return LogError("expected identifier after for");

  std::string IdName = IdentifierStr;
  getNextToken(); // eat identifier.

  if (CurTok != '=')
    return LogError("expected '=' after for");
  getNextToken(); // eat '='.

  auto Start = ParseExpression();
  if (!Start)
    return nullptr;
  if (CurTok != ',')
    return LogError("expected ',' after for start value");
  getNextToken();

  auto End = ParseExpression();
  if (!End)
    return nullptr;

  // The step value is optional.
  std::unique_ptr<ExprAST> Step;
  if (CurTok == ',') {
    getNextToken();
    Step = ParseExpression();
    if (!Step)
      return nullptr;
  }

  if (CurTok != tok_in)
    return LogError("expected 'in' after for");
  getNextToken(); // eat 'in'.

  auto Body = ParseExpression();
  if (!Body)
    return nullptr;

  return llvm::make_unique<ForExprAST>(IdName, std::move(Start), std::move(End),
                                       std::move(Step), std::move(Body));
}

/// primary
///   ::= identifierexpr
///   ::= numberexpr
///   ::= parenexpr
///   ::= ifexpr
///   ::= forexpr
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
  case tok_if:
    return ParseIfExpr();
  case tok_for:
    return ParseForExpr();
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

Value *IfExprAST::codegen() {
  Value *CondV = Cond->codegen();
  if (!CondV)
    return nullptr;

  // Convert condition to a bool by comparing non-equal to 0.0.
  CondV = Builder.CreateFCmpONE(
      CondV, ConstantFP::get(TheContext, APFloat(0.0)), "ifcond");

  Function *TheFunction = Builder.GetInsertBlock()->getParent();

  // Create blocks for the then and else cases.  Insert the 'then' block at the
  // end of the function.
  BasicBlock *ThenBB = BasicBlock::Create(TheContext, "then", TheFunction);
  BasicBlock *ElseBB = BasicBlock::Create(TheContext, "else");
  BasicBlock *MergeBB = BasicBlock::Create(TheContext, "ifcont");

  Builder.CreateCondBr(CondV, ThenBB, ElseBB);

  // Emit then value.
  Builder.SetInsertPoint(ThenBB);

  Value *ThenV = Then->codegen();
  if (!ThenV)
    return nullptr;

  Builder.CreateBr(MergeBB);
  // Codegen of 'Then' can change the current block, update ThenBB for the PHI.
  ThenBB = Builder.GetInsertBlock();

  // Emit else block.
  TheFunction->getBasicBlockList().push_back(ElseBB);
  Builder.SetInsertPoint(ElseBB);

  Value *ElseV = Else->codegen();
  if (!ElseV)
    return nullptr;

  Builder.CreateBr(MergeBB);
  // Codegen of 'Else' can change the current block, update ElseBB for the PHI.
  ElseBB = Builder.GetInsertBlock();

  // Emit merge block.
  TheFunction->getBasicBlockList().push_back(MergeBB);
  Builder.SetInsertPoint(MergeBB);
  PHINode *PN = Builder.CreatePHI(Type::getDoubleTy(TheContext), 2, "iftmp");

  PN->addIncoming(ThenV, ThenBB);
  PN->addIncoming(ElseV, ElseBB);
  return PN;
}

// Output for-loop as:
//   ...
//   start = startexpr
//   goto loop
// loop:
//   variable = phi [start, loopheader], [nextvariable, loopend]
//   ...
//   bodyexpr
//   ...
// loopend:
//   step = stepexpr
//   nextvariable = variable + step
//   endcond = endexpr
//   br endcond, loop, endloop
// outloop:
Value *ForExprAST::codegen() {
  // Emit the start code first, without 'variable' in scope.
  Value *StartVal = Start->codegen();
  if (!StartVal)
    return nullptr;

  // Make the new basic block for the loop header, inserting after current
  // block.
  Function *TheFunction = Builder.GetInsertBlock()->getParent();
  BasicBlock *PreheaderBB = Builder.GetInsertBlock();
  BasicBlock *LoopBB = BasicBlock::Create(TheContext, "loop", TheFunction);

  // Insert an explicit fall through from the current block to the LoopBB.
  Builder.CreateBr(LoopBB);

  // Start insertion in LoopBB.
  Builder.SetInsertPoint(LoopBB);

  // Start the PHI node with an entry for Start.
  PHINode *Variable =
      Builder.CreatePHI(Type::getDoubleTy(TheContext), 2, VarName);
  Variable->addIncoming(StartVal, PreheaderBB);

  // Within the loop, the variable is defined equal to the PHI node.  If it
  // shadows an existing variable, we have to restore it, so save it now.
  Value *OldVal = NamedValues[VarName];
  NamedValues[VarName] = Variable;

  // Emit the body of the loop.  This, like any other expr, can change the
  // current BB.  Note that we ignore the value computed by the body, but don't
  // allow an error.
  if (!Body->codegen())
    return nullptr;

  // Emit the step value.
  Value *StepVal = nullptr;
  if (Step) {
    StepVal = Step->codegen();
    if (!StepVal)
      return nullptr;
  } else {
    // If not specified, use 1.0.
    StepVal = ConstantFP::get(TheContext, APFloat(1.0));
  }

  Value *NextVar = Builder.CreateFAdd(Variable, StepVal, "nextvar");

  // Compute the end condition.
  Value *EndCond = End->codegen();
  if (!EndCond)
    return nullptr;

  // Convert condition to a bool by comparing non-equal to 0.0.
  EndCond = Builder.CreateFCmpONE(
      EndCond, ConstantFP::get(TheContext, APFloat(0.0)), "loopcond");

  // Create the "after loop" block and insert it.
  BasicBlock *LoopEndBB = Builder.GetInsertBlock();
  BasicBlock *AfterBB =
      BasicBlock::Create(TheContext, "afterloop", TheFunction);

  // Insert the conditional branch into the end of LoopEndBB.
  Builder.CreateCondBr(EndCond, LoopBB, AfterBB);

  // Any new code will be inserted in AfterBB.
  Builder.SetInsertPoint(AfterBB);

  // Add a new entry to the PHI node for the backedge.
  Variable->addIncoming(NextVar, LoopEndBB);

  // Restore the unshadowed variable.
  if (OldVal)
    NamedValues[VarName] = OldVal;
  else
    NamedValues.erase(VarName);

  // for expr always returns 0.0.
  return Constant::getNullValue(Type::getDoubleTy(TheContext));
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