# LLVM

LLVM is used as a target for the jam compiler. This contains the emitter used to convert Lekvar to llvm-ir.

## Approach

The current approach for emitting llvm-ir using Lekvar uses a file-like object as a target output. The final output target is used as a global write target for llvm-ir. Since emitting can jump from one function to the next without finishing, writing has to be buffered using a stack of strings, where the top of the stack is always the writing target and when removed is written to the global output.

This approach is sub-optimal because of the mass-use of string addition, especially with the python implementation but it is good enough for now.

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
