---
title: '6. Kaleidoscope: Extending the Language: User-defined Operators'
date: 2018-01-12 20:44:41
tags: LLVM Tutorial
---

## 6.1. Chapter 6 Introduction

欢迎来到“[用LLVM实现一门编程语言](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)”教程第6章。教程到了现在，我们已经有了一个函数式的编程语言，虽然它的功能很少，但已经可以使用了。然而，还有一个很大的问题没有解决。我们的语言目前缺少很多有用的运算符（比如除法、逻辑否，以及除了小于以外的任何二元比较运算符）。

<!-- more -->

<!-- Welcome to Chapter 6 of the “[Implementing a language with LLVM](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)” tutorial. At this point in our tutorial, we now have a fully functional language that is fairly minimal, but also useful. There is still one big problem with it, however. Our language doesn’t have many useful operators (like division, logical negation, or even any comparisons besides less-than). -->

这一章将会增加用户定义的运算符，这使得Kaleidoscope不再那么简洁和优雅。某种程度上来说，这一章的改变将带给我们一门简洁丑陋的语言，但同时也是一门强大的语言。创建你自己的编程语言的一个好处是你可以决定什么好，什么不好。在我们的教程中我们将用这种方式来展示有趣的语法分析技术。

<!-- This chapter of the tutorial takes a wild digression into adding user-defined operators to the simple and beautiful Kaleidoscope language. This digression now gives us a simple and ugly language in some ways, but also a powerful one at the same time. One of the great things about creating your own language is that you get to decide what is good or bad. In this tutorial we’ll assume that it is okay to use this as a way to show some interesting parsing techniques. -->

在教程最后，我们将会运行一个Kaleidoscope语言的样例程序[renders the Mandelbrot set](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl06.html#kicking-the-tires)。这是一个让你了解你可以用Kaleidoscope做什么以及Kaleidoscope的特性的例子。

<!-- At the end of this tutorial, we’ll run through an example Kaleidoscope application that [renders the Mandelbrot set](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl06.html#kicking-the-tires). This gives an example of what you can build with Kaleidoscope and its feature set. -->

## 6.2. User-defined Operators: the Idea

我们将在Kaleidoscope中添加的“过多的运算符”比C++等语言的运算符更一般化。在C++中，你只能重定义已有的运算符：你不能修改语法，不能引入新的运算符，不能修改优先级，等等。在这一章中，我们将为Kaleidoscope增加这样的能力，让用户充实一下语言所支持的运算符。

<!-- The “operator overloading” that we will add to Kaleidoscope is more general than in languages like C++. In C++, you are only allowed to redefine existing operators: you can’t programmatically change the grammar, introduce new operators, change precedence levels, etc. In this chapter, we will add this capability to Kaleidoscope, which will let the user round out the set of operators that are supported. -->

教程中这部分像这样添加用户定义的运算符展示了手写语法分析的能力和灵活性。目前为止，我们实现的语法分析器使用递归下降的方法处理大部分的语法，用运算符优先文法对表达式进行语法分析。具体细节请看[Chapter 2](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl02.html)。使用运算符优先文法，可以让程序员很方便地在语法中添加新的运算符：在JIT运行时语法是动态可扩展的。

<!-- The point of going into user-defined operators in a tutorial like this is to show the power and flexibility of using a hand-written parser. Thus far, the parser we have been implementing uses recursive descent for most parts of the grammar and operator precedence parsing for the expressions. See [Chapter 2](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl02.html) for details. By using operator precedence parsing, it is very easy to allow the programmer to introduce new operators into the grammar: the grammar is dynamically extensible as the JIT runs. -->

我们将要添加的两个具体特性是可编程一元运算符（至今为止Kaleidoscope完全没有一元运算符）和二元运算符。下面是一个例子：

<!-- The two specific features we’ll add are programmable unary operators (right now, Kaleidoscope has no unary operators at all) as well as binary operators. An example of this is: -->

```
# Logical unary not.
def unary!(v)
  if v then
    0
  else
    1;

# Define > with the same precedence as <.
def binary> 10 (LHS RHS)
  RHS < LHS;

# Binary "logical or", (note that it does not "short circuit")
def binary| 5 (LHS RHS)
  if LHS then
    1
  else if RHS then
    1
  else
    0;

# Define = with slightly lower precedence than relationals.
def binary= 9 (LHS RHS)
  !(LHS < RHS | LHS > RHS);
```

许多编程语言希望能够在语言内部实现自己的标准运行库。在Kaleidoscope中，我们在库中实现语言很重要的部分。

<!-- Many languages aspire to being able to implement their standard runtime library in the language itself. In Kaleidoscope, we can implement significant parts of the language in the library! -->

我们将这些特性分成两部分实现：实现用户定义的二元运算符以及增加一元运算符。

<!-- We will break down implementation of these features into two parts: implementing support for user-defined binary operators and adding unary operators. -->

## 6.3. User-defined Binary Operators

用我们现在的框架增加用户定义二元运算符的支持是相当简单的。首先我们增加一元/二元关键字：

<!-- Adding support for user-defined binary operators is pretty simple with our current framework. We’ll first add support for the unary/binary keywords: -->

```C++
enum Token {
  ...
  // operators
  tok_binary = -11,
  tok_unary = -12
};
...
static int gettok() {
...
    if (IdentifierStr == "for")
      return tok_for;
    if (IdentifierStr == "in")
      return tok_in;
    if (IdentifierStr == "binary")
      return tok_binary;
    if (IdentifierStr == "unary")
      return tok_unary;
    return tok_identifier;
```

上面的代码只在词法分析器中增加了一元和二元关键字，就像我们在[previous chapters](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl5.html#lexer-extensions-for-if-then-else)中做的那样。我们现在的AST的一个很好的特点是，二元运算符全部用它们的ASCII码值作为opcode。我们扩展运算符时，也将使用相同的表示方法，所以我们不需要一个新的AST或者语法分析器。

<!-- This just adds lexer support for the unary and binary keywords, like we did in [previous chapters](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl5.html#lexer-extensions-for-if-then-else). One nice thing about our current AST, is that we represent binary operators with full generalisation by using their ASCII code as the opcode. For our extended operators, we’ll use this same representation, so we don’t need any new AST or parser support. -->

另一方面，我们需要表示这些新运算符的定义，在函数定义中的“def binary| 5”部分。在我们至今的语法中，函数定义的“name”作为“原型”进行语法分析，并保存到`PrototypeAST` AST节点中。为了将我们新定义的运算符表示为原型，我们必须如下扩展`PrototypeAST` AST节点：

<!-- On the other hand, we have to be able to represent the definitions of these new operators, in the “def binary| 5” part of the function definition. In our grammar so far, the “name” for the function definition is parsed as the “prototype” production and into the `PrototypeAST` AST node. To represent our new user-defined operators as prototypes, we have to extend the `PrototypeAST` AST node like this: -->

```C++
/// PrototypeAST - This class represents the "prototype" for a function,
/// which captures its argument names as well as if it is an operator.
class PrototypeAST {
  std::string Name;
  std::vector<std::string> Args;
  bool IsOperator;
  unsigned Precedence;  // Precedence if a binary op.

public:
  PrototypeAST(const std::string &name, std::vector<std::string> Args,
               bool IsOperator = false, unsigned Prec = 0)
  : Name(name), Args(std::move(Args)), IsOperator(IsOperator),
    Precedence(Prec) {}

  Function *codegen();
  const std::string &getName() const { return Name; }

  bool isUnaryOp() const { return IsOperator && Args.size() == 1; }
  bool isBinaryOp() const { return IsOperator && Args.size() == 2; }

  char getOperatorName() const {
    assert(isUnaryOp() || isBinaryOp());
    return Name[Name.size() - 1];
  }

  unsigned getBinaryPrecedence() const { return Precedence; }
};
```

基本思路是，现在出了要知道prototype的名称外，我们还要追踪，看它是否是一个运算符，如果是的话，它的优先级是多少。优先级只适用于二元运算符（下面将会看到，优先级不用于一元运算符）。现在，我们有表示用户定义运算符的原型的方法了，我们需要进行语法分析：

<!-- Basically, in addition to knowing a name for the prototype, we now keep track of whether it was an operator, and if it was, what precedence level the operator is at. The precedence is only used for binary operators (as you’ll see below, it just doesn’t apply for unary operators). Now that we have a way to represent the prototype for a user-defined operator, we need to parse it: -->

```C++
/// prototype
///   ::= id '(' id* ')'
///   ::= binary LETTER number? (id, id)
static std::unique_ptr<PrototypeAST> ParsePrototype() {
  std::string FnName;

  unsigned Kind = 0;  // 0 = identifier, 1 = unary, 2 = binary.
  unsigned BinaryPrecedence = 30;

  switch (CurTok) {
  default:
    return LogErrorP("Expected function name in prototype");
  case tok_identifier:
    FnName = IdentifierStr;
    Kind = 0;
    getNextToken();
    break;
  case tok_binary:
    getNextToken();
    if (!isascii(CurTok))
      return LogErrorP("Expected binary operator");
    FnName = "binary";
    FnName += (char)CurTok;
    Kind = 2;
    getNextToken();

    // Read the precedence if present.
    if (CurTok == tok_number) {
      if (NumVal < 1 || NumVal > 100)
        return LogErrorP("Invalid precedence: must be 1..100");
      BinaryPrecedence = (unsigned)NumVal;
      getNextToken();
    }
    break;
  }

  if (CurTok != '(')
    return LogErrorP("Expected '(' in prototype");

  std::vector<std::string> ArgNames;
  while (getNextToken() == tok_identifier)
    ArgNames.push_back(IdentifierStr);
  if (CurTok != ')')
    return LogErrorP("Expected ')' in prototype");

  // success.
  getNextToken();  // eat ')'.

  // Verify right number of names for operator.
  if (Kind && ArgNames.size() != Kind)
    return LogErrorP("Invalid number of operands for operator");

  return llvm::make_unique<PrototypeAST>(FnName, std::move(ArgNames), Kind != 0,
                                         BinaryPrecedence);
}
```

这些都是比较直观的语法分析的代码，我们之前已经有很多类似的代码了。这段代码有意思的一个部分是为二元运算符设置`FnName`的几行。举例来说，它会为新定义的“@”运算符构造类似于“binary@”的名字。然后，它会利用LLVM symbol table中的symbol names允许任意字符（包括空字符）的特点。

<!-- This is all fairly straightforward parsing code, and we have already seen a lot of similar code in the past. One interesting part about the code above is the couple lines that set up `FnName` for binary operators. This builds names like “binary@” for a newly defined “@” operator. It then takes advantage of the fact that symbol names in the LLVM symbol table are allowed to have any character in them, including embedded nul characters. -->

下一个要添加的有意思的事情是，为这些二元运算符添加codegen支持。在我们当前的结构中，这是一次很简单的添加，只需要我们已有的二元运算符节点增加一个default case即可。

<!-- The next interesting thing to add, is codegen support for these binary operators. Given our current structure, this is a simple addition of a default case for our existing binary operator node: -->

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
    break;
  }

  // If it wasn't a builtin binary operator, it must be a user defined one. Emit
  // a call to it.
  Function *F = getFunction(std::string("binary") + Op);
  assert(F && "binary operator not found!");

  Value *Ops[2] = { L, R };
  return Builder.CreateCall(F, Ops, "binop");
}
```

正如你在上面看到的那样，新代码实际上很简单。它知识在symbol table中搜索一个合适的运算符，并且生成一个调用它的函数。因为用户定义的运算符会按照常规的函数构造（因为“prototype” boils down to a function with the right name），everything falls into place。

<!-- As you can see above, the new code is actually really simple. It just does a lookup for the appropriate operator in the symbol table and generates a function call to it. Since user-defined operators are just built as normal functions (because the “prototype” boils down to a function with the right name) everything falls into place. -->

最后一部分代码我们省略了，is a bit of top-level magic：

<!-- The final piece of code we are missing, is a bit of top-level magic: -->

```C++
Function *FunctionAST::codegen() {
  // Transfer ownership of the prototype to the FunctionProtos map, but keep a
  // reference to it for use below.
  auto &P = *Proto;
  FunctionProtos[Proto->getName()] = std::move(Proto);
  Function *TheFunction = getFunction(P.getName());
  if (!TheFunction)
    return nullptr;

  // If this is an operator, install it.
  if (P.isBinaryOp())
    BinopPrecedence[P.getOperatorName()] = P.getBinaryPrecedence();

  // Create a new basic block to start insertion into.
  BasicBlock *BB = BasicBlock::Create(TheContext, "entry", TheFunction);
  ...
```

本质上来说，在codegen一个函数钱，如果它是一个用户定义的运算符，我们将它注册在优先级表中。This allows the binary operator parsing logic we already have in place to handle it. Since we are working on a fully-general operator precedence parser, this is all we need to do to “extend the grammar”.

<!-- Basically, before codegening a function, if it is a user-defined operator, we register it in the precedence table. This allows the binary operator parsing logic we already have in place to handle it. Since we are working on a fully-general operator precedence parser, this is all we need to do to “extend the grammar”. -->

现在我们有强力的用户定义的二元运算符了。大部分工作基于我们前面为其它运算符构造的框架。增加一元运算符会更有挑战，因为我们至今没有任何框架——让我们看看它需要哪些工作吧。

<!-- Now we have useful user-defined binary operators. This builds a lot on the previous framework we built for other operators. Adding unary operators is a bit more challenging, because we don’t have any framework for it yet - lets see what it takes. -->

## 6.4. User-defined Unary Operators

因为我们现在还没有在Kaleidoscope语言中增加一元运算符的支持，我们首先将添加用来支持它们的所有东西。上面我们在词法分析器中增加了对‘unary’关键字的简单支持。除此之外，我们需要一个AST节点：

<!-- Since we don’t currently support unary operators in the Kaleidoscope language, we’ll need to add everything to support them. Above, we added simple support for the ‘unary’ keyword to the lexer. In addition to that, we need an AST node: -->

```C++
/// UnaryExprAST - Expression class for a unary operator.
class UnaryExprAST : public ExprAST {
  char Opcode;
  std::unique_ptr<ExprAST> Operand;

public:
  UnaryExprAST(char Opcode, std::unique_ptr<ExprAST> Operand)
    : Opcode(Opcode), Operand(std::move(Operand)) {}

  Value *codegen() override;
};
```

这个AST节点很简单，也很显而易见。它相当于直接复制了二元运算符的AST节点，除了它只有一个child以外。这些做完后，我们需要添加语法分析逻辑。对一元运算符进行语法分析很简单：我们将为它增加一个新函数：

<!-- This AST node is very simple and obvious by now. It directly mirrors the binary operator AST node, except that it only has one child. With this, we need to add the parsing logic. Parsing a unary operator is pretty simple: we’ll add a new function to do it: -->

```C++
/// unary
///   ::= primary
///   ::= '!' unary
static std::unique_ptr<ExprAST> ParseUnary() {
  // If the current token is not an operator, it must be a primary expr.
  if (!isascii(CurTok) || CurTok == '(' || CurTok == ',')
    return ParsePrimary();

  // If this is a unary operator, read it.
  int Opc = CurTok;
  getNextToken();
  if (auto Operand = ParseUnary())
    return llvm::make_unique<UnaryExprAST>(Opc, std::move(Operand));
  return nullptr;
}
```

我们在这里添加的语法很直观。当对一个primary operator进行语法分析时，如果看到一个一元运算符，我们将这个运算符吃掉，作为一个前缀，然后将剩下的部分作为另一个一元运算符进行语法分析。这就允许我们处理多个一元运算符（比如“!!x“）。注意，一元运算符不能像二元运算符那样有歧义，所以不需要优先级。

<!-- The grammar we add is pretty straightforward here. If we see a unary operator when parsing a primary operator, we eat the operator as a prefix and parse the remaining piece as another unary operator. This allows us to handle multiple unary operators (e.g. ”!!x”). Note that unary operators can’t have ambiguous parses like binary operators can, so there is no need for precedence information. -->

这个函数的问题时我们需要在某处调用ParseUnary。为此，我们修改了之前ParsePrimary的调用者，用ParseUnary替换：

<!-- The problem with this function, is that we need to call ParseUnary from somewhere. To do this, we change previous callers of ParsePrimary to call ParseUnary instead: -->

```C++
/// binoprhs
///   ::= ('+' unary)*
static std::unique_ptr<ExprAST> ParseBinOpRHS(int ExprPrec,
                                              std::unique_ptr<ExprAST> LHS) {
  ...
    // Parse the unary expression after the binary operator.
    auto RHS = ParseUnary();
    if (!RHS)
      return nullptr;
  ...
}
/// expression
///   ::= unary binoprhs
///
static std::unique_ptr<ExprAST> ParseExpression() {
  auto LHS = ParseUnary();
  if (!LHS)
    return nullptr;

  return ParseBinOpRHS(0, std::move(LHS));
}
```

有了这两个简单的修改后，现在我们可以对一元运算符进行语法分析，并从中构造AST了。下一步，为了对一元运算符原型进行语法分析，我们需要增加原型的语法支持。我们用下面的代码扩展二元运算符的代码：

<!-- With these two simple changes, we are now able to parse unary operators and build the AST for them. Next up, we need to add parser support for prototypes, to parse the unary operator prototype. We extend the binary operator code above with: -->

```C++
/// prototype
///   ::= id '(' id* ')'
///   ::= binary LETTER number? (id, id)
///   ::= unary LETTER (id)
static std::unique_ptr<PrototypeAST> ParsePrototype() {
  std::string FnName;

  unsigned Kind = 0;  // 0 = identifier, 1 = unary, 2 = binary.
  unsigned BinaryPrecedence = 30;

  switch (CurTok) {
  default:
    return LogErrorP("Expected function name in prototype");
  case tok_identifier:
    FnName = IdentifierStr;
    Kind = 0;
    getNextToken();
    break;
  case tok_unary:
    getNextToken();
    if (!isascii(CurTok))
      return LogErrorP("Expected unary operator");
    FnName = "unary";
    FnName += (char)CurTok;
    Kind = 1;
    getNextToken();
    break;
  case tok_binary:
    ...
```

As with binary operators, we name unary operators with a name that includes the operator character。这会在代码生成的时候帮到我们。提到代码生成，我们最后需要增加的一段代码就是为一元运算符增加codegen支持。代码长成下面这个样子：

<!-- As with binary operators, we name unary operators with a name that includes the operator character. This assists us at code generation time. Speaking of, the final piece we need to add is codegen support for unary operators. It looks like this: -->

```C++
Value *UnaryExprAST::codegen() {
  Value *OperandV = Operand->codegen();
  if (!OperandV)
    return nullptr;

  Function *F = getFunction(std::string("unary") + Opcode);
  if (!F)
    return LogErrorV("Unknown unary operator");

  return Builder.CreateCall(F, OperandV, "unop");
}
```

和二元运算符相比，上面的代码很相似，但更简单。它更简单的原因主要是它不需要处理任何预定义的运算符。

<!-- This code is similar to, but simpler than, the code for binary operators. It is simpler primarily because it doesn’t need to handle any predefined operators. -->

## 6.5. Kicking the Tires

尽管有些难以置信，但完成我们在前面的章节里提到的一些扩展后，我们开发出了一门实际可用的编程语言。我们现在可以用它做很多有意思的事情，包括I/O，数学计算，以及很多其他的事情。举例来说，我们现在可以增加一个nice sequencing operator（printd被定义为打印一个具体的值，并切换到新一行）：

<!-- It is somewhat hard to believe, but with a few simple extensions we’ve covered in the last chapters, we have grown a real-ish language. With this, we can do a lot of interesting things, including I/O, math, and a bunch of other things. For example, we can now add a nice sequencing operator (printd is defined to print out the specified value and a newline): -->

```
ready> extern printd(x);
Read extern:
declare double @printd(double)

ready> def binary : 1 (x y) 0;  # Low-precedence operator that ignores operands.
...
ready> printd(123) : printd(456) : printd(789);
123.000000
456.000000
789.000000
Evaluated to 0.000000
```

我们同样可以定义很多“原创的”的运算符，比如：

<!-- We can also define a bunch of other “primitive” operations, such as: -->

```
# Logical unary not.
def unary!(v)
  if v then
    0
  else
    1;

# Unary negate.
def unary-(v)
  0-v;

# Define > with the same precedence as <.
def binary> 10 (LHS RHS)
  RHS < LHS;

# Binary logical or, which does not short circuit.
def binary| 5 (LHS RHS)
  if LHS then
    1
  else if RHS then
    1
  else
    0;

# Binary logical and, which does not short circuit.
def binary& 6 (LHS RHS)
  if !LHS then
    0
  else
    !!RHS;

# Define = with slightly lower precedence than relationals.
def binary = 9 (LHS RHS)
  !(LHS < RHS | LHS > RHS);

# Define ':' for sequencing: as a low-precedence operator that ignores operands
# and just returns the RHS.
def binary : 1 (x y) y;
```

有了前面的if/then/else的支持后，我们可以为I/O定义一些有趣的函数。比如说，下面的代码会打印字符，“density”反映了输入的值：值越低，字符越密集。

<!-- Given the previous if/then/else support, we can also define interesting functions for I/O. For example, the following prints out a character whose “density” reflects the value passed in: the lower the value, the denser the character: -->

```
ready> extern putchard(char);
...
ready> def printdensity(d)
  if d > 8 then
    putchard(32)  # ' '
  else if d > 4 then
    putchard(46)  # '.'
  else if d > 2 then
    putchard(43)  # '+'
  else
    putchard(42); # '*'
...
ready> printdensity(1): printdensity(2): printdensity(3):
       printdensity(4): printdensity(5): printdensity(9):
       putchard(10);
**++.
Evaluated to 0.000000
```

基于这些简单的原创操作符，我们可以定义更有趣的东西。比如说这里是一个短小的函数，决定

Based on these simple primitive operations, we can start to define more interesting things. For example, here’s a little function that determines the number of iterations it takes for a certain function in the complex plane to diverge:

```
# Determine whether the specific location diverges.
# Solve for z = z^2 + c in the complex plane.
def mandelconverger(real imag iters creal cimag)
  if iters > 255 | (real*real + imag*imag > 4) then
    iters
  else
    mandelconverger(real*real - imag*imag + creal,
                    2*real*imag + cimag,
                    iters+1, creal, cimag);

# Return the number of iterations required for the iteration to escape
def mandelconverge(real imag)
  mandelconverger(real, imag, 0, real, imag);
```

This “`z = z2 + c`” function is a beautiful little creature that is the basis for computation of the [Mandelbrot Set](http://en.wikipedia.org/wiki/Mandelbrot_set). Our `mandelconverge` function returns the number of iterations that it takes for a complex orbit to escape, saturating to 255. This is not a very useful function by itself, but if you plot its value over a two-dimensional plane, you can see the Mandelbrot set. Given that we are limited to using putchard here, our amazing graphical output is limited, but we can whip together something using the density plotter above:

```
# Compute and plot the mandelbrot set with the specified 2 dimensional range
# info.
def mandelhelp(xmin xmax xstep   ymin ymax ystep)
  for y = ymin, y < ymax, ystep in (
    (for x = xmin, x < xmax, xstep in
       printdensity(mandelconverge(x,y)))
    : putchard(10)
  )

# mandel - This is a convenient helper function for plotting the mandelbrot set
# from the specified position with the specified Magnification.
def mandel(realstart imagstart realmag imagmag)
  mandelhelp(realstart, realstart+realmag*78, realmag,
             imagstart, imagstart+imagmag*40, imagmag);
```

Given this, we can try plotting out the mandelbrot set! Lets try it out:

```
ready> mandel(-2.3, -1.3, 0.05, 0.07);
*******************************+++++++++++*************************************
*************************+++++++++++++++++++++++*******************************
**********************+++++++++++++++++++++++++++++****************************
*******************+++++++++++++++++++++.. ...++++++++*************************
*****************++++++++++++++++++++++.... ...+++++++++***********************
***************+++++++++++++++++++++++.....   ...+++++++++*********************
**************+++++++++++++++++++++++....     ....+++++++++********************
*************++++++++++++++++++++++......      .....++++++++*******************
************+++++++++++++++++++++.......       .......+++++++******************
***********+++++++++++++++++++....                ... .+++++++*****************
**********+++++++++++++++++.......                     .+++++++****************
*********++++++++++++++...........                    ...+++++++***************
********++++++++++++............                      ...++++++++**************
********++++++++++... ..........                        .++++++++**************
*******+++++++++.....                                   .+++++++++*************
*******++++++++......                                  ..+++++++++*************
*******++++++.......                                   ..+++++++++*************
*******+++++......                                     ..+++++++++*************
*******.... ....                                      ...+++++++++*************
*******.... .                                         ...+++++++++*************
*******+++++......                                    ...+++++++++*************
*******++++++.......                                   ..+++++++++*************
*******++++++++......                                   .+++++++++*************
*******+++++++++.....                                  ..+++++++++*************
********++++++++++... ..........                        .++++++++**************
********++++++++++++............                      ...++++++++**************
*********++++++++++++++..........                     ...+++++++***************
**********++++++++++++++++........                     .+++++++****************
**********++++++++++++++++++++....                ... ..+++++++****************
***********++++++++++++++++++++++.......       .......++++++++*****************
************+++++++++++++++++++++++......      ......++++++++******************
**************+++++++++++++++++++++++....      ....++++++++********************
***************+++++++++++++++++++++++.....   ...+++++++++*********************
*****************++++++++++++++++++++++....  ...++++++++***********************
*******************+++++++++++++++++++++......++++++++*************************
*********************++++++++++++++++++++++.++++++++***************************
*************************+++++++++++++++++++++++*******************************
******************************+++++++++++++************************************
*******************************************************************************
*******************************************************************************
*******************************************************************************
Evaluated to 0.000000
ready> mandel(-2, -1, 0.02, 0.04);
**************************+++++++++++++++++++++++++++++++++++++++++++++++++++++
***********************++++++++++++++++++++++++++++++++++++++++++++++++++++++++
*********************+++++++++++++++++++++++++++++++++++++++++++++++++++++++++.
*******************+++++++++++++++++++++++++++++++++++++++++++++++++++++++++...
*****************+++++++++++++++++++++++++++++++++++++++++++++++++++++++++.....
***************++++++++++++++++++++++++++++++++++++++++++++++++++++++++........
**************++++++++++++++++++++++++++++++++++++++++++++++++++++++...........
************+++++++++++++++++++++++++++++++++++++++++++++++++++++..............
***********++++++++++++++++++++++++++++++++++++++++++++++++++........        .
**********++++++++++++++++++++++++++++++++++++++++++++++.............
********+++++++++++++++++++++++++++++++++++++++++++..................
*******+++++++++++++++++++++++++++++++++++++++.......................
******+++++++++++++++++++++++++++++++++++...........................
*****++++++++++++++++++++++++++++++++............................
*****++++++++++++++++++++++++++++...............................
****++++++++++++++++++++++++++......   .........................
***++++++++++++++++++++++++.........     ......    ...........
***++++++++++++++++++++++............
**+++++++++++++++++++++..............
**+++++++++++++++++++................
*++++++++++++++++++.................
*++++++++++++++++............ ...
*++++++++++++++..............
*+++....++++................
*..........  ...........
*
*..........  ...........
*+++....++++................
*++++++++++++++..............
*++++++++++++++++............ ...
*++++++++++++++++++.................
**+++++++++++++++++++................
**+++++++++++++++++++++..............
***++++++++++++++++++++++............
***++++++++++++++++++++++++.........     ......    ...........
****++++++++++++++++++++++++++......   .........................
*****++++++++++++++++++++++++++++...............................
*****++++++++++++++++++++++++++++++++............................
******+++++++++++++++++++++++++++++++++++...........................
*******+++++++++++++++++++++++++++++++++++++++.......................
********+++++++++++++++++++++++++++++++++++++++++++..................
Evaluated to 0.000000
ready> mandel(-0.9, -1.4, 0.02, 0.03);
*******************************************************************************
*******************************************************************************
*******************************************************************************
**********+++++++++++++++++++++************************************************
*+++++++++++++++++++++++++++++++++++++++***************************************
+++++++++++++++++++++++++++++++++++++++++++++**********************************
++++++++++++++++++++++++++++++++++++++++++++++++++*****************************
++++++++++++++++++++++++++++++++++++++++++++++++++++++*************************
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++**********************
+++++++++++++++++++++++++++++++++.........++++++++++++++++++*******************
+++++++++++++++++++++++++++++++....   ......+++++++++++++++++++****************
+++++++++++++++++++++++++++++.......  ........+++++++++++++++++++**************
++++++++++++++++++++++++++++........   ........++++++++++++++++++++************
+++++++++++++++++++++++++++.........     ..  ...+++++++++++++++++++++**********
++++++++++++++++++++++++++...........        ....++++++++++++++++++++++********
++++++++++++++++++++++++.............       .......++++++++++++++++++++++******
+++++++++++++++++++++++.............        ........+++++++++++++++++++++++****
++++++++++++++++++++++...........           ..........++++++++++++++++++++++***
++++++++++++++++++++...........                .........++++++++++++++++++++++*
++++++++++++++++++............                  ...........++++++++++++++++++++
++++++++++++++++...............                 .............++++++++++++++++++
++++++++++++++.................                 ...............++++++++++++++++
++++++++++++..................                  .................++++++++++++++
+++++++++..................                      .................+++++++++++++
++++++........        .                               .........  ..++++++++++++
++............                                         ......    ....++++++++++
..............                                                    ...++++++++++
..............                                                    ....+++++++++
..............                                                    .....++++++++
.............                                                    ......++++++++
...........                                                     .......++++++++
.........                                                       ........+++++++
.........                                                       ........+++++++
.........                                                           ....+++++++
........                                                             ...+++++++
.......                                                              ...+++++++
                                                                    ....+++++++
                                                                   .....+++++++
                                                                    ....+++++++
                                                                    ....+++++++
                                                                    ....+++++++
Evaluated to 0.000000
ready> ^D
```

At this point, you may be starting to realize that Kaleidoscope is a real and powerful language. It may not be self-similar :), but it can be used to plot things that are!

With this, we conclude the “adding user-defined operators” chapter of the tutorial. We have successfully augmented our language, adding the ability to extend the language in the library, and we have shown how this can be used to build a simple but interesting end-user application in Kaleidoscope. At this point, Kaleidoscope can build a variety of applications that are functional and can call functions with side-effects, but it can’t actually define and mutate a variable itself.

Strikingly, variable mutation is an important feature of some languages, and it is not at all obvious how to [add support for mutable variables](https://releases.llvm.org/5.0.0/docs/tutorial/LangImpl07.html) without having to add an “SSA construction” phase to your front-end. In the next chapter, we will describe how you can add variable mutation without building SSA in your front-end.

## 6.6. Full Code Listing

这里是我们的例子的完整代码，这一章增加了用户定义运算符。用下面的指令build这个例子：

<!-- Here is the complete code listing for our running example, enhanced with the support for user-defined operators. To build this example, use: -->

```bash
# Compile
clang++ -g toy.cpp `llvm-config --cxxflags --ldflags --system-libs --libs core mcjit native` -O3 -o toy
# Run
./toy
```

On some platforms, you will need to specify -rdynamic or -Wl,–export-dynamic when linking. This ensures that symbols defined in the main executable are exported to the dynamic linker and so are available for symbol resolution at run time. This is not needed if you compile your support code into a shared library, although doing that will cause problems on Windows.

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
  tok_in = -10,

  // operators
  tok_binary = -11,
  tok_unary = -12
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
    if (IdentifierStr == "binary")
      return tok_binary;
    if (IdentifierStr == "unary")
      return tok_unary;
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

/// UnaryExprAST - Expression class for a unary operator.
class UnaryExprAST : public ExprAST {
  char Opcode;
  std::unique_ptr<ExprAST> Operand;

public:
  UnaryExprAST(char Opcode, std::unique_ptr<ExprAST> Operand)
      : Opcode(Opcode), Operand(std::move(Operand)) {}

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
/// of arguments the function takes), as well as if it is an operator.
class PrototypeAST {
  std::string Name;
  std::vector<std::string> Args;
  bool IsOperator;
  unsigned Precedence; // Precedence if a binary op.

public:
  PrototypeAST(const std::string &Name, std::vector<std::string> Args,
               bool IsOperator = false, unsigned Prec = 0)
      : Name(Name), Args(std::move(Args)), IsOperator(IsOperator),
        Precedence(Prec) {}

  Function *codegen();
  const std::string &getName() const { return Name; }

  bool isUnaryOp() const { return IsOperator && Args.size() == 1; }
  bool isBinaryOp() const { return IsOperator && Args.size() == 2; }

  char getOperatorName() const {
    assert(isUnaryOp() || isBinaryOp());
    return Name[Name.size() - 1];
  }

  unsigned getBinaryPrecedence() const { return Precedence; }
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

/// Error* - These are little helper functions for error handling.
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

/// unary
///   ::= primary
///   ::= '!' unary
static std::unique_ptr<ExprAST> ParseUnary() {
  // If the current token is not an operator, it must be a primary expr.
  if (!isascii(CurTok) || CurTok == '(' || CurTok == ',')
    return ParsePrimary();

  // If this is a unary operator, read it.
  int Opc = CurTok;
  getNextToken();
  if (auto Operand = ParseUnary())
    return llvm::make_unique<UnaryExprAST>(Opc, std::move(Operand));
  return nullptr;
}

/// binoprhs
///   ::= ('+' unary)*
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

    // Parse the unary expression after the binary operator.
    auto RHS = ParseUnary();
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
///   ::= unary binoprhs
///
static std::unique_ptr<ExprAST> ParseExpression() {
  auto LHS = ParseUnary();
  if (!LHS)
    return nullptr;

  return ParseBinOpRHS(0, std::move(LHS));
}

/// prototype
///   ::= id '(' id* ')'
///   ::= binary LETTER number? (id, id)
///   ::= unary LETTER (id)
static std::unique_ptr<PrototypeAST> ParsePrototype() {
  std::string FnName;

  unsigned Kind = 0; // 0 = identifier, 1 = unary, 2 = binary.
  unsigned BinaryPrecedence = 30;

  switch (CurTok) {
  default:
    return LogErrorP("Expected function name in prototype");
  case tok_identifier:
    FnName = IdentifierStr;
    Kind = 0;
    getNextToken();
    break;
  case tok_unary:
    getNextToken();
    if (!isascii(CurTok))
      return LogErrorP("Expected unary operator");
    FnName = "unary";
    FnName += (char)CurTok;
    Kind = 1;
    getNextToken();
    break;
  case tok_binary:
    getNextToken();
    if (!isascii(CurTok))
      return LogErrorP("Expected binary operator");
    FnName = "binary";
    FnName += (char)CurTok;
    Kind = 2;
    getNextToken();

    // Read the precedence if present.
    if (CurTok == tok_number) {
      if (NumVal < 1 || NumVal > 100)
        return LogErrorP("Invalid precedence: must be 1..100");
      BinaryPrecedence = (unsigned)NumVal;
      getNextToken();
    }
    break;
  }

  if (CurTok != '(')
    return LogErrorP("Expected '(' in prototype");

  std::vector<std::string> ArgNames;
  while (getNextToken() == tok_identifier)
    ArgNames.push_back(IdentifierStr);
  if (CurTok != ')')
    return LogErrorP("Expected ')' in prototype");

  // success.
  getNextToken(); // eat ')'.

  // Verify right number of names for operator.
  if (Kind && ArgNames.size() != Kind)
    return LogErrorP("Invalid number of operands for operator");

  return llvm::make_unique<PrototypeAST>(FnName, ArgNames, Kind != 0,
                                         BinaryPrecedence);
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

Value *UnaryExprAST::codegen() {
  Value *OperandV = Operand->codegen();
  if (!OperandV)
    return nullptr;

  Function *F = getFunction(std::string("unary") + Opcode);
  if (!F)
    return LogErrorV("Unknown unary operator");

  return Builder.CreateCall(F, OperandV, "unop");
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
    break;
  }

  // If it wasn't a builtin binary operator, it must be a user defined one. Emit
  // a call to it.
  Function *F = getFunction(std::string("binary") + Op);
  assert(F && "binary operator not found!");

  Value *Ops[] = {L, R};
  return Builder.CreateCall(F, Ops, "binop");
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

  // If this is an operator, install it.
  if (P.isBinaryOp())
    BinopPrecedence[P.getOperatorName()] = P.getBinaryPrecedence();

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

  if (P.isBinaryOp())
    BinopPrecedence.erase(P.getOperatorName());
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

```
