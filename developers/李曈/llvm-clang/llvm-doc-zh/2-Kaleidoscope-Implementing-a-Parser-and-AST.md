---
title: '2. Kaleidoscope: Implementing a Parser and AST'
date: 2018-01-10 15:46:33
tags: LLVM Tutorial
---

## 2.1. Chapter 2 Introduction

欢迎来到”[用LLVM实现一门程序语言](https://releases.llvm.org/5.0.0/docs/tutorial/index.html)“教程第2章。这一节会展示如何基于Chapter 1构造的词法分析器来为Kaleidoscope语言构造一个完整的[语法分析器](http://en.wikipedia.org/wiki/Parsing)。完成语法分析器后，我们将定义并构造[抽象语法树（AST）](http://en.wikipedia.org/wiki/Abstract_syntax_tree) 。

<!-- more -->

<!--
Welcome to Chapter 2 of the “[Implementing a language with LLVM](http://llvm.org/docs/tutorial/index.html)” tutorial. This chapter shows you how to use the lexer, built in [Chapter 1](http://llvm.org/docs/tutorial/LangImpl01.html), to build a full parser for our Kaleidoscope language. Once we have a [parser](http://en.wikipedia.org/wiki/Parsing), we’ll define and build an [Abstract Syntax Tree](http://en.wikipedia.org/wiki/Abstract_syntax_tree) (AST).
-->

我们将结合[递归下降文法（Recursive Descent Parsing）](http://en.wikipedia.org/wiki/Recursive_descent_parser)与[运算符优先文法（Operator-Precedence Parsing）](http://en.wikipedia.org/wiki/Operator-precedence_parser)来对Kaleidoscope语言进行语法分析（后一个规则用于二元运算表达式，前一个规则用于其余所有情况）。在开始语法分析前，让我们先讨论一下语法分析器的输出：抽象语法树。

<!--
The parser we will build uses a combination of [Recursive Descent Parsing](http://en.wikipedia.org/wiki/Recursive_descent_parser) and [Operator-Precedence Parsing ](http://en.wikipedia.org/wiki/Operator-precedence_parser)to parse the Kaleidoscope language (the latter for binary expressions and the former for everything else). Before we get to parsing though, lets talk about the output of the parser: the Abstract Syntax Tree.
-->

## 2.2. The Abstract Syntax Tree (AST)

一个程序的AST会捕捉该程序的行为，并用一种方便编译器后续阶段（比如说code generation阶段）理解和处理的方式表达出来。我们希望语言中的每次construct都对应一个object，AST应该尽可能精确地对该语言进行建模。在`Kaleidoscope`中，我们有一些表达式，一个原型，以及一个函数object。我们从表达式开始：

<!-- 原文：
The AST for a program captures its behavior in such a way that it is easy for later stages of the compiler (e.g. code generation) to interpret. We basically want one object for each construct in the language, and the AST should closely model the language. In Kaleidoscope, we have expressions, a prototype, and a function object. We’ll start with expressions first 
-->

```C++
/// ExprAST - Base class for all expression nodes.
class ExprAST {
public:
  virtual ~ExprAST() {}
};

/// NumberExprAST - Expression class for numeric literals like "1.0".
class NumberExprAST : public ExprAST {
  double Val;

public:
  NumberExprAST(double Val) : Val(Val) {}
};
```

上面的代码展示了`ExprAST`基类，以及一个用于表示数字常量的子类。值得注意的是`NumberExprAST`类将数字常量的数值存储在实例变量中，这让编译器后面的阶段可以知道存储的数字常量的值。

<!-- comment 原文：
The code above shows the definition of the base ExprAST class and one subclass which we use for numeric literals. The important thing to note about this code is that the NumberExprAST class captures the numeric value of the literal as an instance variable. This allows later phases of the compiler to know what the stored numeric value is.
-->

现在我们只构造了AST，并没有有效的读写访问函数。可以很方便地增加一个虚函数来实现这些功能，比如说，可以打印出代码。下面是一些其他的AST节点定义，我们会在`Kaleidoscope`语言的基本格式中用到：

<!-- comment 原文：
Right now we only create the AST, so there are no useful accessor methods on them. It would be very easy to add a virtual method to pretty print the code, for example. Here are the other expression AST node definitions that we’ll use in the basic form of the Kaleidoscope language:
-->

```C++
/// VariableExprAST - Expression class for referencing a variable, like "a".
class VariableExprAST : public ExprAST {
  std::string Name;

public:
  VariableExprAST(const std::string &Name) : Name(Name) {}
};

/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
  char Op;
  std::unique_ptr<ExprAST> LHS, RHS;

public:
  BinaryExprAST(char op, std::unique_ptr<ExprAST> LHS,
                std::unique_ptr<ExprAST> RHS)
    : Op(op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
};

/// CallExprAST - Expression class for function calls.
class CallExprAST : public ExprAST {
  std::string Callee;
  std::vector<std::unique_ptr<ExprAST>> Args;

public:
  CallExprAST(const std::string &Callee,
              std::vector<std::unique_ptr<ExprAST>> Args)
    : Callee(Callee), Args(std::move(Args)) {}
};
```

这些代码都（故意地）很直观：变量保存着变量名，二元运算符保存着它们的运算符(比如：‘+’)，函数调用保存调用者的函数名，以及参数表达式的列表。AST的一个优点在于，它可以在不涉及语言的句法的前提下，表述语言的特点。要注意，这里没有讨论运算符优先级、词法结构等问题。

<!--
This is all (intentionally) rather straight-forward: variables capture the variable name, binary operators capture their opcode (e.g. ‘+’), and calls capture a function name as well as a list of any argument expressions. One thing that is nice about our AST is that it captures the language features without talking about the syntax of the language. Note that there is no discussion about precedence of binary operators, lexical structure, etc
-->

对于我们基本的程序语言来说，这些都是我们将要定义的表达式节点。因为还没有条件控制流，所以我们还没有结束，在后面的小节里会补充上。我们现在要做两件事：怎样描述函数接口，以及怎样描述函数本身。

<!--
For our basic language, these are all of the expression nodes we’ll define. Because it doesn’t have conditional control flow, it isn’t Turing-complete; we’ll fix that in a later installment. The two things we need next are a way to talk about the interface to a function, and a way to talk about functions themselves:
-->

```C++
/// PrototypeAST - This class represents the "prototype" for a function,
/// which captures its name, and its argument names (thus implicitly the number
/// of arguments the function takes).
class PrototypeAST {
  std::string Name;
  std::vector<std::string> Args;

public:
  PrototypeAST(const std::string &name, std::vector<std::string> Args)
    : Name(name), Args(std::move(Args)) {}

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
};
```

在Kaleidoscope语言中，函数的输入只伴随着一列参数。因为所有的变量都是双精度浮点型，所以不需要存储变量类型。在更先进、更实际的语言中，`ExprAST`类会要一个type域。

<!--
In Kaleidoscope, functions are typed with just a count of their arguments. Since all values are double precision floating point, the type of each argument doesn’t need to be stored anywhere. In a more aggressive and realistic language, the “ExprAST” class would probably have a type field.
->

有了这些基本的工具，我们可以开始讨论语法表达式，以及Kaleidoscope中的函数体了。

<!--
With this scaffolding, we can now talk about parsing expressions and function bodies in Kaleidoscope.
-->

## 2.3. Parser Basics

现在我们需要定义一个语法分析器去构造AST。基本的思路是对类似于“x+y”(词法分析会返回3个token)的东西进行语法分析，通过类似于下面的函数调用转换成AST：

<!--
Now that we have an AST to build, we need to define the parser code to build it. The idea here is that we want to parse something like “x+y” (which is returned as three tokens by the lexer) into an AST that could be generated with calls like this:
-->

```C++
auto LHS = llvm::make_unique<VariableExprAST>("x");
auto RHS = llvm::make_unique<VariableExprAST>("y");
auto Result = std::make_unique<BinaryExprAST>('+', std::move(LHS),
                                              std::move(RHS));
```

为了做到这一点，我们需要定义一些基本的功能代码块：

<!--
In order to do this, we’ll start by defining some basic helper routines:
-->

```C++
/// CurTok/getNextToken - Provide a simple token buffer.  CurTok is the current
/// token the parser is looking at.  getNextToken reads another token from the
/// lexer and updates CurTok with its results.
static int CurTok;
static int getNextToken() {
  return CurTok = gettok();
}
```

上面的代码实现了一个简单的token buffer。它可以从词法分析的结果中获取下一个token。语法分析的所有函数都假设`CurTok`是当前需要进行语法分析的token。

<!--
This implements a simple token buffer around the lexer. This allows us to look one token ahead at what the lexer is returning. Every function in our parser will assume that CurTok is the current token that needs to be parsed.
-->

```C++
/// LogError* - These are little helper functions for error handling.
std::unique_ptr<ExprAST> LogError(const char *Str) {
  fprintf(stderr, "LogError: %s\n", Str);
  return nullptr;
}
std::unique_ptr<PrototypeAST> LogErrorP(const char *Str) {
  LogError(Str);
  return nullptr;
}
```

`LogError`这部分的代码在我们语法分析器中用于处理errors，我们语法分析器中的error恢复部分并不是最好的，也并不user-friendly，但对于tutorial足够了。这些代码使得有不同返回类型的代码路径处理errors变得更简单：它们总是返回null。

<!--
The `LogError` routines are simple helper routines that our parser will use to handle errors. The error recovery in our parser will not be the best and is not particular user-friendly, but it will be enough for our tutorial. These routines make it easier to handle errors in routines that have various return types: they always return null.
-->

有了这些基本的函数，我们可以实现我们算法的第一部分：数值字面量。

<!--
With these basic helper functions, we can implement the first piece of our grammar: numeric literals.
-->

## 2.4. Basic Expression Parsing

因为数字字面量是最容易处理的，所以我们从它开始。对于语法中的每种production，我们都会定义一个函数来对它进行语法分析。处理数字字面量的函数如下：

<!--
We start with numeric literals, because they are the simplest to process. For each production in our grammar, we’ll define a function which parses that production. For numeric literals, we have:
-->

```C++
/// numberexpr ::= number
static std::unique_ptr<ExprAST> ParseNumberExpr() {
  auto Result = llvm::make_unique<NumberExprAST>(NumVal);
  getNextToken(); // consume the number
  return std::move(Result);
}
```

这段代码非常简单：它在当前token是`tok_number`时被调用。它读取当前数字的值，创建一个`NumberExprAST`节点，让词法分析器向前，读取下一个token，然后返回。

<!--
This routine is very simple: it expects to be called when the current token is a `tok_number` token. It takes the current number value, creates a `NumberExprAST` node, advances the lexer to the next token, and finally returns.
-->

这里有一些有意思的点，其中最重要的一点是这些代码都会读取当前production的所有tokens，并且设置词法分析器的buffer（也就是`CurTok`）中刚好下一个要处理token（这个token不属于当前的语法production）。这是递归下降文法中比较常规的方法。圆括号操作符的定义是一个更好的例子，代码如下：

<!--
There are some interesting aspects to this. The most important one is that this routine eats all of the tokens that correspond to the production and returns the lexer buffer with the next token (which is not part of the grammar production) ready to go. This is a fairly standard way to go for recursive descent parsers. For a better example, the parenthesis operator is defined like this:
-->

```C++
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
```

这个函数展示了语法分析器有意思的几个地方：

<!--
This function illustrates a number of interesting things about the parser:
-->

1）它向我们展示了如何使用LogError。这个函数被调用时，当前的token是'('，分析完子表达式后，应该有一个')'。比如说，如果用户输入"(4 x"，而不是"(4)"，那么语法分析器就应该报错。语法分析器需要一种方式，来指出哪里发生了错误：在我们的语法分析器中，出错时会返回null。

<!--
1) It shows how we use the LogError routines. When called, this function expects that the current token is a ‘(‘ token, but after parsing the subexpression, it is possible that there is no ‘)’ waiting. For example, if the user types in “(4 x” instead of “(4)”, the parser should emit an error. Because errors can occur, the parser needs a way to indicate that they happened: in our parser, we return null on an error.
-->

2）另一个有意思的地方是这个函数通过调用`ParseExpression`来递归调用（稍后我们会看到`ParseExpression`可以调用`ParseParenExpr`）。这一点很powerful，因为它可以处理递归语法，让每个production都比较简单。注意圆括号本身并不创建AST节点，圆括号最重要的功能是指导语法分析，并提供分组。一旦语法分析器构造好了AST，就不再需要圆括号了。

<!--
2) Another interesting aspect of this function is that it uses recursion by calling `ParseExpression` (we will soon see that `ParseExpression` can call `ParseParenExpr`). This is powerful because it allows us to handle recursive grammars, and keeps each production very simple. Note that parentheses do not cause construction of AST nodes themselves. While we could do it this way, the most important role of parentheses are to guide the parser and provide grouping. Once the parser constructs the AST, parentheses are not needed.
-->

下一个production用来处理变量引用，以及函数调用：

<!--
The next simple production is for handling variable references and function calls:
-->

```C++
/// identifierexpr
///   ::= identifier
///   ::= identifier '(' expression* ')'
static std::unique_ptr<ExprAST> ParseIdentifierExpr() {
  std::string IdName = IdentifierStr;

  getNextToken();  // eat identifier.

  if (CurTok != '(') // Simple variable ref.
    return llvm::make_unique<VariableExprAST>(IdName);

  // Call.
  getNextToken();  // eat (
  std::vector<std::unique_ptr<ExprAST>> Args;
  if (CurTok != ')') {
    while (1) {
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
```

这段代码的风格和之前的代码一样（这段代码在当前token是`tok_identifier`时被调用）。这段代码同样有递归调用和错误处理部分。一个有意思的地方是，这段代码通过*look-ahead*的方法来判定当前的标识符是一个变量的引用还是一个函数调用。具体来说，就是往前多读一个token，看这个token是不是'('，如果不是，构造`VariableExprAST`节点；如果是，构造`CallExprAST`节点。现在，我们有了简单的对表达式进行语法分析的代码，可以把它们包装在一个函数中，这样就可以通过一个入口来进行语法分析。我们把这类表达式称为"primary"表达式，原因会在[后面的章节](http://llvm.org/docs/tutorial/LangImpl6.html#user-defined-unary-operators)里说明。为了对任意primary表达式进行语法分析，我们需要定义表达式的排序：

<!--
This routine follows the same style as the other routines. (It expects to be called if the current token is a `tok_identifier` token). It also has recursion and error handling. One interesting aspect of this is that it uses *look-ahead* to determine if the current identifier is a stand alone variable reference or if it is a function call expression. It handles this by checking to see if the token after the identifier is a ‘(‘ token, constructing either a `VariableExprAST` or `CallExprAST` node as appropriate.
Now that we have all of our simple expression-parsing logic in place, we can define a helper function to wrap it together into one entry point. We call this class of expressions “primary” expressions, for reasons that will become more clear [later in the tutorial](http://llvm.org/docs/tutorial/LangImpl6.html#user-defined-unary-operators). In order to parse an arbitrary primary expression, we need to determine what sort of expression it is:
-->

```C++
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
```

看到上面这个函数后，你就更清楚我们为何可以在不同的函数中对CurTok进行假设。这段代码通过look-ahead来决定表达式检查的顺序，然后通过函数调用来对其进行语法分析。

<!--
Now that you see the definition of this function, it is more obvious why we can assume the state of CurTok in the various functions. This uses look-ahead to determine which sort of expression is being inspected, and then parses it with a function call.
-->

现在基本的表达式已经可以处理了，下面需要处理二元运算表达式了，这会稍微复杂点。

<!--
Now that basic expressions are handled, we need to handle binary expressions. They are a bit more complex.
-->

## 2.5. Binary Expressions Parsing

对二元表达式进行语法分析比较困难，因为它们通常都有多种含义。举例来说，对于“x+y\*z”，语法分析器需要选择将它翻译成“(x+y)\*z”还是“x+(y\*z)”。根据数学知识，我们期望得到后面一种结果，因为乘法的优先级比加法高。

<!--
Binary expressions are significantly harder to parse because they are often ambiguous. For example, when given the string “x+y\*z”, the parser can choose to parse it as either “(x+y)\*z” or “x+(y\*z)”. With common definitions from mathematics, we expect the later parse, because “*” (multiplication) has higher precedence than “+” (addition).
-->

有很多方法可以处理这件事，但是一个优雅且高效的方法是使用[运算符优先文法](http://en.wikipedia.org/wiki/Operator-precedence_parser)。这个技术使用二元运算符的优先级来指导递归调用。首先，我们需要一张优先级顺序表：

<!--
There are many ways to handle this, but an elegant and efficient way is to use [Operator-Precedence Parsing](http://en.wikipedia.org/wiki/Operator-precedence_parser). This parsing technique uses the precedence of binary operators to guide recursion. To start with, we need a table of precedences:
-->

```C++
/// BinopPrecedence - This holds the precedence for each binary operator that is
/// defined.
static std::map<char, int> BinopPrecedence;

/// GetTokPrecedence - Get the precedence of the pending binary operator token.
static int GetTokPrecedence() {
  if (!isascii(CurTok))
    return -1;

  // Make sure it's a declared binop.
  int TokPrec = BinopPrecedence[CurTok];
  if (TokPrec <= 0) return -1;
  return TokPrec;
}

int main() {
  // Install standard binary operators.
  // 1 is lowest precedence.
  BinopPrecedence['<'] = 10;
  BinopPrecedence['+'] = 20;
  BinopPrecedence['-'] = 20;
  BinopPrecedence['*'] = 40;  // highest.
  ...
}
```

在简单版的Kaleidoscope语言中，我们只支持4个二元运算符（当然你可以进行扩充）。`GetTokPrecedence`函数返回当前token的优先级，如果当前token不是二元运算符则返回-1。使用map容器可以很容易地增加新的运算符，同时可以更清晰地看出这个算法并不依赖于特定的运算符。但是不用map的话，直接在`GetTokPrecedence`函数中做比较也很容易实现函数的功能（可能直接用固定大小的数组）。

<!--
For the basic form of Kaleidoscope, we will only support 4 binary operators (this can obviously be extended by you, our brave and intrepid reader). The `GetTokPrecedence` function returns the precedence for the current token, or -1 if the token is not a binary operator. Having a map makes it easy to add new operators and makes it clear that the algorithm doesn’t depend on the specific operators involved, but it would be easy enough to eliminate the map and do the comparisons in the `GetTokPrecedence` function. (Or just use a fixed-size array).
-->

有了上面的代码，我们现在可以开始对二元表达式进行语法分析了。运算符优先文法的基本思路是按照potentially ambiguous的二元运算符，将表达式拆成几个部分。用“a+b+(c+d)\*e\*f+g”表达式举例来说，运算符优先文法分析会将这个表达式看做被二元运算符分割开的primary表达式流。这样一来，它会首先对primary表达式“a”进行语法分析，然后会看到[+, b] [+, (c+d)] [\*, e] [\*, f] and [+, g]。注意，因为圆括号属于primary表达式，二元表达式的语法分析不需要考虑类似于(c+d)的嵌套子表达式。

<!-- With the helper above defined, we can now start parsing binary expressions. The basic idea of operator precedence parsing is to break down an expression with potentially ambiguous binary operators into pieces. Consider, for example, the expression “a+b+(c+d)\*e\*f+g”. Operator precedence parsing considers this as a stream of primary expressions separated by binary operators. As such, it will first parse the leading primary expression “a”, then it will see the pairs [+, b] [+, (c+d)] [*, e] [*, f] and [+, g]. Note that because parentheses are primary expressions, the binary expression parser doesn’t need to worry about nested subexpressions like (c+d) at all. -->

首先，一个表达式是primary表达式的话，可能会跟着一系列的[binop,primaryexpr] pairs。

<!-- To start, an expression is a primary expression potentially followed by a sequence of [binop,primaryexpr] pairs: -->

```C++
/// expression
///   ::= primary binoprhs
///
static std::unique_ptr<ExprAST> ParseExpression() {
  auto LHS = ParsePrimary();
  if (!LHS)
    return nullptr;

  return ParseBinOpRHS(0, std::move(LHS));
}
```

`ParseBinOpRHS`函数对这一系列的pairs进行语法分析。It takes a precedence and a pointer to an expression for the part that has been parsed so far。注意，"x"是一个合法的表达式：也就是说，"binoprhs"允许为空，这种情况下直接把输入的表达式返回。在上面的例子中，代码将表达式"a"作为参数传入`ParseBinOpRHS`，当前token为“+”。

<!--
`ParseBinOpRHS` is the function that parses the sequence of pairs for us. It takes a precedence and a pointer to an expression for the part that has been parsed so far. Note that “x” is a perfectly valid expression: As such, “binoprhs” is allowed to be empty, in which case it returns the expression that is passed into it. In our example above, the code passes the expression for “a” into `ParseBinOpRHS` and the current token is “+”.
-->

传入`ParseBinOpRHS`的优先级数值，表明了该函数可以读取的*最低运算符优先级*。举例来说，如果当前的pair stream是[+, x]，而`ParseBinOpRHS`中传入的优先级是40，那么它就不处理任何tokens（因为'+'的优先级仅为20）。根据这个原则，`ParseBinOpRHS`的代码开头如下：

<!--
The precedence value passed into `ParseBinOpRHS` indicates the *minimal operator precedence* that the function is allowed to eat. For example, if the current pair stream is [+, x] and `ParseBinOpRHS` is passed in a precedence of 40, it will not consume any tokens (because the precedence of ‘+’ is only 20). With this in mind, `ParseBinOpRHS` starts with:
-->

```C++
/// binoprhs
///   ::= ('+' primary)*
static std::unique_ptr<ExprAST> ParseBinOpRHS(int ExprPrec,
                                              std::unique_ptr<ExprAST> LHS) {
  // If this is a binop, find its precedence.
  while (1) {
    int TokPrec = GetTokPrecedence();

    // If this is a binop that binds at least as tightly as the current binop,
    // consume it, otherwise we are done.
    if (TokPrec < ExprPrec)
      return LHS;
```

这段代码会获取当前token的优先级，并检测它的值是否太小。因为我们定义不合法的tokens会返回优先级为-1，这样就使得pair-stream在token stream读完所有二元运算符后结束。如果检查成功，我们就知道这个token是一个二元运算符，并且会被包含在这个表达式中：

<!--
This code gets the precedence of the current token and checks to see if it is too low. Because we defined invalid tokens to have a precedence of -1, this check implicitly knows that the pair-stream ends when the token stream runs out of binary operators. If this check succeeds, we know that the token is a binary operator and that it will be included in this expression:
-->

```C++
    // Okay, we know this is a binop.
    int BinOp = CurTok;
    getNextToken();  // eat binop

    // Parse the primary expression after the binary operator.
    auto RHS = ParsePrimary();
    if (!RHS)
      return nullptr;
```

这段代码读取了二元运算符，然后对后面跟着的primary expression进行语法分析。这样就构造了全部的pair，对于我们的例子来说，第一个pair就是[+, b]。

<!--
As such, this code eats (and remembers) the binary operator and then parses the primary expression that follows. This builds up the whole pair, the first of which is [+, b] for the running example.
-->

现在我们对表达式的左边，以及RHS中的一个pair，进行了语法分析，现在我们需要决定表达式应该按照哪种方式来组织。具体来说，我们可以选择"(a+b) binop unparsed"，或者"a + (b binop unparsed)"。为此，我们需要往前看"binop"是什么，用它的优先级和当前运算符的优先级比较（在这里的例子中，当前运算符是‘+’）:

<!--
Now that we parsed the left-hand side of an expression and one pair of the RHS sequence, we have to decide which way the expression associates. In particular, we could have “(a+b) binop unparsed” or “a + (b binop unparsed)”. To determine this, we look ahead at “binop” to determine its precedence and compare it to BinOp’s precedence (which is ‘+’ in this case):
-->

```C++
    // If BinOp binds less tightly with RHS than the operator after RHS, let
    // the pending operator take RHS as its LHS.
    int NextPrec = GetTokPrecedence();
    if (TokPrec < NextPrec) {
```

如果右边“RHS”的binop的优先级小于或等于当前运算符的优先级，我们可以判定圆括号应该被处理为“(a+b) binop ...”。在我们的例子中，当前运算符是“+”，下一个运算符也是“+”，它们有相同的优先级。在这种情况下我们会在AST中创建“a+b”节点，然后继续进行语法分析：

<!--
If the precedence of the binop to the right of “RHS” is lower or equal to the precedence of our current operator, then we know that the parentheses associate as “(a+b) binop ...”. In our example, the current operator is “+” and the next operator is “+”, we know that they have the same precedence. In this case we’ll create the AST node for “a+b”, and then continue parsing:
-->

```C++
      ... if body omitted ...
    }

    // Merge LHS/RHS.
    LHS = llvm::make_unique<BinaryExprAST>(BinOp, std::move(LHS),
                                           std::move(RHS));
  }  // loop around to the top of the while loop.
}
```

在这个例子中，“a+b”会被视为“(a+b)”，然后进入下一循环，且当前token为“+”。下一次循环中，上面的代码会将“(c+d)”作为primary表达式，进行语法分析，这会使得当前的pair为[+, (c+d)]。之后它会判断上面提到的if条件，和右边primary表达式相连的binop是“\*”。在这种情况下，“\*”的优先级高于“+”的优先级，所以会进入if为真的分支。

<!--
In our example above, this will turn “a+b+” into “(a+b)” and execute the next iteration of the loop, with “+” as the current token. The code above will eat, remember, and parse “(c+d)” as the primary expression, which makes the current pair equal to [+, (c+d)]. It will then evaluate the ‘if’ conditional above with “\*” as the binop to the right of the primary. In this case, the precedence of “\*” is higher than the precedence of “+” so the if condition will be entered.
-->

还有一个遗留的重要问题是“if表达式如何能完整地处理RHS”？在我们的例子中，为了正确构造AST，需要获得"(c+d)\*e\*f"作为RHS表达式。实现这个功能的代码却非常简单（从上面两个代码块复制下来的）：

<!--
The critical question left here is “how can the if condition parse the right hand side in full”? In particular, to build the AST correctly for our example, it needs to get all of “(c+d)\*e\*f” as the RHS expression variable. The code to do this is surprisingly simple (code from the above two blocks duplicated for context):
-->

```C++
    // If BinOp binds less tightly with RHS than the operator after RHS, let
    // the pending operator take RHS as its LHS.
    int NextPrec = GetTokPrecedence();
    if (TokPrec < NextPrec) {
      RHS = ParseBinOpRHS(TokPrec+1, std::move(RHS));
      if (!RHS)
        return nullptr;
    }
    // Merge LHS/RHS.
    LHS = llvm::make_unique<BinaryExprAST>(BinOp, std::move(LHS),
                                           std::move(RHS));
  }  // loop around to the top of the while loop.
}
```

现在，我们知道了连接primary表达式的RHS的二元运算符比我们当前处理的binop的优先级更高。这样一来，所有优先级比“+”高的pairs都会进行语法分析，作为"RHS"返回。为了做到这一点，我们循环调用`ParseBinOpRHS`函数，并将"TokPrec+1"作为最小优先级。在我们的例子中，会返回“(c+d)\*e\*f”作为RHS，它稍后将会设置为“+”表达式的RHS。

<!--
At this point, we know that the binary operator to the RHS of our primary has higher precedence than the binop we are currently parsing. As such, we know that any sequence of pairs whose operators are all higher precedence than “+” should be parsed together and returned as “RHS”. To do this, we recursively invoke the `ParseBinOpRHS` function specifying “TokPrec+1” as the minimum precedence required for it to continue. In our example above, this will cause it to return the AST node for “(c+d)\*e\*f” as RHS, which is then set as the RHS of the ‘+’ expression.
-->

最后，在while循环的下一次迭代中，会对“+g”进行语法分析，并添加到AST中。我们只用了很少的代码（14行）就完整处理了对二元表达式进行语法分析的工作，非常优雅。这里只是对代码的一个粗略的浏览，有的地方还欠缺考虑。我们推荐你用一些比较难的样例去测试，看是否work。

<!--
Finally, on the next iteration of the while loop, the “+g” piece is parsed and added to the AST. With this little bit of code (14 non-trivial lines), we correctly handle fully general binary expression parsing in a very elegant way. This was a whirlwind tour of this code, and it is somewhat subtle. I recommend running through it with a few tough examples to see how it works.
-->

这些就是对处理表达式的代码。现在，我们可以对任意token串进行语法分析，并从中构造表达式。接下来我们要处理函数定义等部分。

<!-- This wraps up handling of expressions. At this point, we can point the parser at an arbitrary token stream and build an expression from it, stopping at the first token that is not part of the expression. Next up we need to handle function definitions, etc. -->

## 2.6. Parsing the Rest

接下来的事情是处理函数原型。在Kaleidoscope中，它们被用在'extern'函数和函数体定义中。做这件事的代码很直观，not interesting：

<!--
The next thing missing is handling of function prototypes. In Kaleidoscope, these are used both for ‘extern’ function declarations as well as function body definitions. The code to do this is straight-forward and not very interesting (once you’ve survived expressions):
-->

```C++
/// prototype
///   ::= id '(' id* ')'
static std::unique_ptr<PrototypeAST> ParsePrototype() {
  if (CurTok != tok_identifier)
    return LogErrorP("Expected function name in prototype");

  std::string FnName = IdentifierStr;
  getNextToken();

  if (CurTok != '(')
    return LogErrorP("Expected '(' in prototype");

  // Read the list of argument names.
  std::vector<std::string> ArgNames;
  while (getNextToken() == tok_identifier)
    ArgNames.push_back(IdentifierStr);
  if (CurTok != ')')
    return LogErrorP("Expected ')' in prototype");

  // success.
  getNextToken();  // eat ')'.

  return llvm::make_unique<PrototypeAST>(FnName, std::move(ArgNames));
}
```

这样一来，函数定义就很简单了，一个函数原型加上函数体表达式的实现：

<!--
Given this, a function definition is very simple, just a prototype plus an expression to implement the body:
-->

```C++
/// definition ::= 'def' prototype expression
static std::unique_ptr<FunctionAST> ParseDefinition() {
  getNextToken();  // eat def.
  auto Proto = ParsePrototype();
  if (!Proto) return nullptr;

  if (auto E = ParseExpression())
    return llvm::make_unique<FunctionAST>(std::move(Proto), std::move(E));
  return nullptr;
}
```

另外，我们支持'extern'定义函数，比如'sin'、'cos'等，我们也支持[前置声明](http://www.learncpp.com/cpp-tutorial/19-header-files/)，这些'extern'只是原型，没有函数体。

<!--
In addition, we support ‘extern’ to declare functions like ‘sin’ and ‘cos’ as well as to support forward declaration of user functions. These ‘extern’s are just prototypes with no body:
-->

```C++
/// external ::= 'extern' prototype
static std::unique_ptr<PrototypeAST> ParseExtern() {
  getNextToken();  // eat extern.
  return ParsePrototype();
}
```

最后，我们也允许用户输入任意顶层表达式，并动态地计算它们。我们将通过为它们定义匿名零参数函数的方法处理这些表达式。

<!-- Finally, we’ll also let the user type in arbitrary top-level expressions and evaluate them on the fly. We will handle this by defining anonymous nullary (zero argument) functions for them: -->

```C++
/// toplevelexpr ::= expression
static std::unique_ptr<FunctionAST> ParseTopLevelExpr() {
  if (auto E = ParseExpression()) {
    // Make an anonymous proto.
    auto Proto = llvm::make_unique<PrototypeAST>("", std::vector<std::string>());
    return llvm::make_unique<FunctionAST>(std::move(Proto), std::move(E));
  }
  return nullptr;
}
```

现在，我们有了所有的代码片段，可以看是构造一个小的driver，运行我们的代码了！

<!--
Now that we have all the pieces, let’s build a little driver that will let us actually execute this code we’ve built!
-->

## 2.7. The Driver

这个小的driver只是在顶层做一个循环的分发，根据token类型调用不同的函数。这里没有太多有意思的点，所以我们只包含了一个顶层循环。下面是“Top-Level Parsing”部分的全部代码。

<!--
The driver for this simply invokes all of the parsing pieces with a top-level dispatch loop. There isn’t much interesting here, so I’ll just include the top-level loop. See below for full code in the “Top-Level Parsing” section.
-->

```C++
/// top ::= definition | external | expression | ';'
static void MainLoop() {
  while (1) {
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
```

这部分代码最有意思的地方在于我们忽略了顶层的分号。你可能会问为什么要这样。简单来说，如果你在命令行中输入“4 + 5”，语法分析器不知道你的输入是否结束。比如说，你可能在下一行输入“def foo...“，这种情况下4+5是一个顶层表达式的结尾；你也可能输入”\*6“，在这种况下这个表达式还没结束。加入顶层分号的话，你可以输入”4+5;“，语法分析器就知道你的输入结束啦。

<!-- The most interesting part of this is that we ignore top-level semicolons. Why is this, you ask? The basic reason is that if you type “4 + 5” at the command line, the parser doesn’t know whether that is the end of what you will type or not. For example, on the next line you could type “def foo...” in which case 4+5 is the end of a top-level expression. Alternatively you could type “* 6”, which would continue the expression. Having top-level semicolons allows you to type “4+5;”, and the parser will know you are done. -->

## 2.8. Conclusions

仅仅用了400行带注释的代码（不带注释和空行的话只需要240行），我们就完成了我们最简化的语言，包含一个词法分析器，一个语法分析器，一个AST构造器。这些做完后，我们就可以执行并验证Kaleidoscope代码，检查语法错误。比如下面的几个简单的交互：

<!--
With just under 400 lines of commented code (240 lines of non-comment, non-blank code), we fully defined our minimal language, including a lexer, parser, and AST builder. With this done, the executable will validate Kaleidoscope code and tell us if it is grammatically invalid. For example, here is a sample interaction:
-->

```C++
$ ./a.out
ready> def foo(x y) x+foo(y, 4.0);
Parsed a function definition.
ready> def foo(x y) x+y y;
Parsed a function definition.
Parsed a top-level expr
ready> def foo(x y) x+y );
Parsed a function definition.
Error: unknown token when expecting an expression
ready> extern sin(a);
ready> Parsed an extern
ready> ^D
$
```

这里还有很多可以扩展的空间，你可以定义新的AST节点，在很多方面扩展这个语言等等。在下一节，我们会展示如何从AST生成LLVM中间码（IR）。

<!--
There is a lot of room for extension here. You can define new AST nodes, extend the language in many ways, etc. In the [next installment](http://llvm.org/docs/tutorial/LangImpl03.html), we will describe how to generate LLVM Intermediate Representation (IR) from the AST.
-->

## 2.9. Full Code Listing

这里是前两小节的完整代码。这段代码是完全独立的，你不需要LLVM或者任何外部的库，只需要C和C++标准库。你可以用下面的命令build这段代码：

<!--
Here is the complete code listing for this and the previous chapter. Note that it is fully self-contained: you don’t need LLVM or any external libraries at all for this. (Besides the C and C++ standard libraries, of course.) To build this, just compile with:
-->

```bash
# Compile
clang++ -g -O3 -std=c++11 toy.cpp
# Run
./a.out
```

* 译者注1：原文档中的编译命令是`clang++ -g -O3 toy.cpp`，在Ubuntu 16.04的环境中测试会报出需要使用c++11的选项，需要加上`-std=c++11`才能顺利编译。
* 译者注2："llvm/ADT/STLExtras.h"是必须的，但这就需要LLVM的库函数了，并不像文档里所说的只需要C和C++标注库。
* 译者注3：这里还有一个小的C++知识点，调用C++标准库时需要加`std::`来指明命名空间，但调用`strtod`、`fprintf`等C标准库时不加。
* 译者注4：AST的定义那一段代码，使用了匿名命名空间。因为AST的相关类在编译器的其它代码里会有，为防止冲突，使用了匿名命名空间来控制作用域。
* 译者注5：代码中用`llvm::make_unique`来构造一个非数组类型T，并返回一个unique_ptr。看起来可以用`std::make_unique`替代，而且这样一来就真的不用包含llvm的库了，只需C/C++标准库即可编译。关于这个问题，[stackoverflow上有一个解答](https://stackoverflow.com/questions/35900866/what-is-the-purpose-of-llvmmake-unique)：`std::make_unique`是C++14新增的，这里用的是C++11。以后有空了可以使用C++14和`std::make_unique`试试。

下面是代码：

<!--
Here is the code:
-->

```C++
#include "llvm/ADT/STLExtras.h"
#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <memory>
#include <string>
#include <vector>

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
};

/// NumberExprAST - Expression class for numeric literals like "1.0".
class NumberExprAST : public ExprAST {
  double Val;

public:
  NumberExprAST(double Val) : Val(Val) {}
};

/// VariableExprAST - Expression class for referencing a variable, like "a".
class VariableExprAST : public ExprAST {
  std::string Name;

public:
  VariableExprAST(const std::string &Name) : Name(Name) {}
};

/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
  char Op;
  std::unique_ptr<ExprAST> LHS, RHS;

public:
  BinaryExprAST(char Op, std::unique_ptr<ExprAST> LHS,
                std::unique_ptr<ExprAST> RHS)
      : Op(Op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
};

/// CallExprAST - Expression class for function calls.
class CallExprAST : public ExprAST {
  std::string Callee;
  std::vector<std::unique_ptr<ExprAST>> Args;

public:
  CallExprAST(const std::string &Callee,
              std::vector<std::unique_ptr<ExprAST>> Args)
      : Callee(Callee), Args(std::move(Args)) {}
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
    LHS = llvm::make_unique<BinaryExprAST>(BinOp, std::move(LHS),
                                           std::move(RHS));
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
// Top-Level parsing
//===----------------------------------------------------------------------===//

static void HandleDefinition() {
  if (ParseDefinition()) {
    fprintf(stderr, "Parsed a function definition.\n");
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}

static void HandleExtern() {
  if (ParseExtern()) {
    fprintf(stderr, "Parsed an extern\n");
  } else {
    // Skip token for error recovery.
    getNextToken();
  }
}

static void HandleTopLevelExpression() {
  // Evaluate a top-level expression into an anonymous function.
  if (ParseTopLevelExpr()) {
    fprintf(stderr, "Parsed a top-level expr\n");
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

  // Run the main "interpreter loop" now.
  MainLoop();

  return 0;
}
```