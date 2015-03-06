.. _lekvar-builtins:

Lekvar Builtins
###############

Builtins is a module provided by both the frontend and the backend that is
accessible from all scopes and by default included.

The backend must supply specified functions that abstract the low level
functions. Ideally these functions could be inlined during optimisation,
removing the overhead of a function call.

Backend Builtins
================

::

    module _builtins
        class Byte
        def intAdd(Byte[n], Byte[n]) infer n
        def floatAdd(Byte[n], Byte[n]) infer n
        def intSub(Byte[n], Byte[n]) infer n
        def floatSub(Byte[n], Byte[n]) infer n
        def intMul(Byte[n], Byte[n]) infer n
        def floatMul(Byte[n], Byte[n]) infer n
        def intDiv(Byte[n], Byte[n]) infer n
        def floatDiv(Byte[n], Byte[n]) infer n
        def intMod(Byte[n], Byte[n]) infer n
        def floatMod(Byte[n], Byte[n]) infer n
        def leftShift(Byte[n], Byte[n]) infer n
        def logicalRightShift(Byte[n], Byte[n]) infer n
        def arithmeticRightShift(Byte[n], Byte[n]) infer n
        def and(Byte[n], Byte[n]) infer n
        def or(Byte[n], Byte[n]) infer n
        def xor(Byte[n], Byte[n]) infer n
    end
