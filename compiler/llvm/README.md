# LLVM

LLVM is used as a target for the jam compiler. This contains the emitter used to convert lekvar to llvm bytecode.

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
}

define void @lekvar.main.helloWorld() {
    call i32 @puts(i8* getelementptr inbounds ([13 x i8]* @temp.1, i32 0, i32 0))
}

define i32 @main() {
    call i32 @lekvar.main()
    ret i32 0
}
```
