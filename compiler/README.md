# The Compiler

This folder contains the current implementations of the jam lexer, the jam parser, lekvar, the lekvar verifier and the lekvar llvm emitter. It also contains a set of tests these modules need to pass.

## Design

Since each component is supposed to be separable, the following would be the ideal way to run each component:

```
lekvar_ir = jam.compile(source)
lekvar_ir.verify()
llvm_ir = lekvar_ir.emit(llvm)
```
