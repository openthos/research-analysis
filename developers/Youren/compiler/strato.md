# Reading notes for strato
Strato: A Retargetable Framework for Low-Level Inlined-Reference Monitors

## 出发点
之前的工作都是基于底层汇编代码的，这样的工作通常是有一个rewriter 一个verifier，针对的是同一套指令集，通常同时开发。但是这样导致这个工作和某个特定的指令集绑定了起来，同时这种工作优化也比较困难。
因此这篇工作希望能够做一个IR层面的security check。
在IR层面做有两个好处，一个是IR层面的代码可以很容易的编译成各种平台的代码，另一个好处是可以重用很多信息，导致优化更简单。

这样做的缺点是，IR层做是将llvm 的代码都作为TCB了，代码数量过多导致bug 更容易发生，另一方面，是后端代码生成时可能会break security check。因此需要对产生的代码进行验证。
因此，工作的挑战就在于如何执行IR层的rewriting ，同时保证底层还是安全的。

## 工作流程
	1. 编译器前段
	2. 编译器优化
	3. 插入检查点
	4. 检查点优化
	5. 生成代码
	6. Constraint 检查，如果一个constraint 在编译和优化的过程中失效了，则将check 保留，否则移除掉
	7. 检查lowering  测试底层代码中怎么实现security check性能最好。
	8. 验证 一个独立的verifier验证底层的代码。

去除不必要的data checking：
	1. Redundant check elimination
	2. Sequential memory access
	3. loop-based optimization

### Redundant check elimination
因为检查指令是对pointer 的存取进行检查的。因此如果一个pointer 在之前被check过，而check之后这个pointer没有写回到内存中，那么我们就认为对这个pointer 的之后的check可以省略。
但是一直到机器码之前是不知道pointer 有没有被写回的，因此只是在ir 码中加入注释，写constraint。

	 
### Sequential Memory access Optimization
因为存在guard zone，而如果是数组寻址的话，基地址和偏移量如果一定不会超过guardzone，就没关系。但是偏移量和机器实现有关（例如x86平台，long 在32位机器上是32位，在64位机器上是64位）
### Loop检查
在loop前面加入check。如果该循环体内的check 可以省略，则之后省略
