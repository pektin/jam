Lambdas
#######

Lambdas are identical to :doc:`methods`, except that they are anonymous and
therefore cannot be overloaded. They provide a quicker syntax for defining
small, limited use methods.

Syntax
======

.. productionlist::
    LambdaArgumentList: "(" [ `Argument` [ "," `Argument` ]* ] ")"
    LambdaArguments: `LambdaArgumentList` | `Argument`
    Lambda: [`LambdaArguments`] "=>" `Value`

Example
=======
::

    array = [1, 2, 3, 4]

    array.map(a => a**2) #=> [1, 4, 9, 16]

    array.reduce((a, b) => a*b) #=> 24

    a = => puts("hi")
    12.times(a)
