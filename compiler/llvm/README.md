# LLVM

LLVM is used as a target for the jam compiler. This contains the emitter used to convert Lekvar to llvm-ir.

## Approach

The current approach uses a ctypes binding to the LLVM C bindings. Each lekvar class is extended to include a ``emitValue`` function, which should return a ``llvm.Value`` (``LLVMValueRef``) instance. ``lekvar.ScopeObject`` classes are extended to also include a ``emit`` function, which creates the lekvar object, without returning a value. ``lekvar.Type`` classes are extended to further include a ``emitType`` function, which should return a ``llvm.Type`` (``LLVMTypeRef``) instance.

## Example

Input (Python, to make it understandable)

```
def helloWorld():
    puts("Hello World!")
helloWorld()
```

Output (LLVM IR)

```
declare i32 @puts(i8*)

@temp.1 = internal constant [13 x i8] c"Hello World!\00"

define void @lekvar.main() {
    call void @lekvar.helloWorld()
    ret void
}

define void @lekvar.main.helloWorld() {
    call i32 @puts(i8* getelementptr inbounds ([13 x i8]* @temp.1, i32 0, i32 0))
    ret void
}

define i32 @main() {
    call i32 @lekvar.main()
    ret i32 0
}
```
