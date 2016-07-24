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

    [1, 2, 3, 4].map(a => a**2) #=> [1, 4, 9, 16]
    [1, 2, 3, 4].reduce((a, b) => a*b) #=> 24
    12.times(=> puts("Hi"))
