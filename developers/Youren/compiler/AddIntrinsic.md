在添加Intrinsic的过程中学习了很多内容，同时也遇见了许多bug
为了添加Intrinsic 主要参考以下链接
http://lists.llvm.org/pipermail/llvm-dev/2015-October/091685.html
其次是Extend llvm
https://llvm.org/docs/ExtendingLLVM.html
为了能够正确的修改td文件，添加intrinsic， 还需要学习tablegen 的功能与作用
https://llvm.org/docs/TableGen/index.html

首先明白，每一个td 文件最后都要生成成一个C++文件，而TD文件（tablegen）的存在，就是一个类似高级模板的功能，将很多重复的东西合并在一起，在TD中只要写不同的地方，剩下的就可以自动生成。

这个文档中描述tablegen 主要的数据包括records ，records 可以详细归类为class和definition。

Records 是一个个有着unique name ，a list of value 和 a list of superclasses。 List of values 是tablegen 工具主要生成的内容。
其中definition 就是具体的 records了，一个definition 通常不存在任何的未定义的不确定的值，有着def 关键字

而classes是一个抽象的records，用来描述和建立其他的 records。

所以我们在看td文件的时候，关于用什么参数去定义自己的数据，需要去看你的def 继承与哪个类，这个类的参数有哪些。
比如需要定义一个intrinsic，那么intrinsic 怎么定义呢，可以参考其他的intrinsic 定义。例如：
```
  let TargetPrefix = "x86" in {
    def int_x86_seh_lsda : Intrinsic<[llvm_ptr_ty], [llvm_ptr_ty], [IntrNoMem]>;

    // Marks the EH registration node created in LLVM IR prior to code generation.
    def int_x86_seh_ehregnode : Intrinsic<[], [llvm_ptr_ty], []>;

    // Marks the EH guard slot node created in LLVM IR prior to code generation.
    def int_x86_seh_ehguard : Intrinsic<[], [llvm_ptr_ty], []>;

    // Given a pointer to the end of an EH registration object, returns the true
    // parent frame address that can be used with llvm.localrecover.
    def int_x86_seh_recoverfp : Intrinsic<[llvm_ptr_ty],
                                          [llvm_ptr_ty, llvm_ptr_ty],
                                          [IntrNoMem]>;
  }
```
但是他们的定义各个部分是什么意思呢？去找intrinsic 类的定义，这个类的定义是C++ 写的，如下：
```
class Intrinsic<list<LLVMType> ret_types,
                list<LLVMType> param_types = [],
                list<IntrinsicProperty> intr_properties = [],
                string name = "",
                list<SDNodeProperty> sd_properties = []> : SDPatternOperator {
  string LLVMName = name;
  string TargetPrefix = "";   // Set to a prefix for target-specific intrinsics.
  list<LLVMType> RetTypes = ret_types;
  list<LLVMType> ParamTypes = param_types;
  list<IntrinsicProperty> IntrProperties = intr_properties;
  let Properties = sd_properties;

  bit isTarget = 0;
}
```
由此我们可以知道，intrinsic 第一个参数是返回值，第二个是 各个参数的类型，第三个是 这个intrinsic 的各种特性，可以在代码或者文档中找到各个特性的解释：
https://github.com/llvm-mirror/llvm/blob/master/include/llvm/IR/Intrinsics.td

同样，在这个文件中还可以找到td 中的各个类型的定义。

依据上面的intrinsic的参数，我们写出我们想要添加的 check函数如下：

```
def int_x86_checkload:Intrinsic<[],[llvm_ptr_ty],[]>;
def int_x86_checkstore:Intrinsic<[],[llvm_ptr_ty],[]>;
```

另外在Target/X86里面的 i32 i32mem 之类的，都是在X86InstrInfo.td下面的新的def
包括addr， GR64等等。

之后添加 对Intrinsic 自动转换伪指令的代码  
```
let isPseudo = 1 in {
 def checkload : PseudoI<(outs), (ins i64mem:$src),
                         [(int_x86_checkload addr:$src)]>;
 def checkstore : PseudoI<(outs), (ins i64mem:$src),
                         [(int_x86_checkstore addr:$src)]>;  
}
```
在这里定义checkload 是一条伪指令，他的输出为空，输入是一个i64mem  
之后的是pattern match。 表示如果遇见了这个pattern，则将其转换为ispsudo  

以下是实现的时候的各种bug：  

如果遇见的错误是Intrinsic 没有自动转换为pseudo，那么可能是pattern match 写错了，可能是pseudo 的参数写错了。目前不知道怎么找到具体应该怎么写，这个写法是参考别的Intrinsic和pseudo的定义，实验出来的。
如果出现以下错误，是处理pseudo的太早了。应放在ExpandPseudo 里面正好。
```
Stack dump:
0.      Program arguments: /home/shenyouren/workspace/build-llvm/bin/llc -o obj/simple.s obj/simple-opt.bc
1.      Running pass 'Function Pass Manager' on module 'obj/simple-opt.bc'.
2.      Running pass 'Unnamed pass: implement Pass::getPassName()' on function '@travelBB'
#0 0x0000000002561dcb llvm::sys::PrintStackTrace(llvm::raw_ostream&) /home/shenyouren/workspace/llvm/lib/Support/Unix/Signals.inc:398
```
