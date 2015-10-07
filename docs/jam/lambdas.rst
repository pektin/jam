Lambdas
#######

Lambdas are identical to :doc:`methods<methods>`, except that they are anonymous
and therefore cannot be overloaded. They provide a quicker syntax for defining
small, one use methods.

Syntax
======

.. productionlist::
    Lambda: "(" [ [`Argument` ","]* `Argument` ] ")" "=>" `Value`

Example
=======

::

    map((a) => a**2, [1, 2, 3, 4]) #=> [1, 4, 9, 16]
    reduce((a, b) => a*b, [1, 2, 3, 4]) #=> 24
