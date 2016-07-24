Methods
#######

A method is a scoped group of instructions as a value, that may be executed
given any number of arguments as input and that may output any number of values.
A method may be overloaded with different kinds of inputs or outputs.

The input of a method comes in the form of a collection of variables called
arguments. Input to a method must match exactly one overload.

A method must be defined with a name (see. :doc:`lambdas` for anonymous methods)
and can be overloaded with multiple definitions.

At any point in the method a return statement may be made to cause the method to
complete and take the given value as the output of the method call. When the
return value of a method is explicitly defined, all possible execution paths
must end with a return statement.

Methods are also valid values, and can thus be assigned to :doc:`variables`. A
variable that is of a method type may be assigned any methods with compatible
overloads.

.. seealso::

    :doc:`lambdas`
        Another kind of method

Type Inference
==============

Method arguments may be defined without a type. In this case, the type is
determined by every action involving that argument. From this it builds a "type
expectation" that is used at compile time to check whether arguments are valid.

For instance, if a method is defined as::

    def intAdd(x, y) -> Int
      return x + y
    end

Then the type expectation of ``x`` is that it has a method ``+`` that can take
one argument ``y`` and returns a type compatible with ``Int``.

Syntax
======

.. productionlist::
    Argument: `Variable` [ "=" `Value` ]
    MethodPrototype: `Identifier` "(" [ `Argument` [ "," `Argument` ]* ] ")" [ "->" `Value` ]
    Return: "return" [`Value`]
    MethodInstruction: `Instruction` | `Return`
    MethodInstructionSet: ( `MethodInstruction` \n )*
    Method: "def" `MethodPrototype` `MethodInstructionSet` "end"

Examples
========

::

    def double(x:Float) -> Float
      return x * 2
    end

    def double(x) -> Int
      return x * 2
    end

    def double()
      return 2
    end

    double(2) #=> 4
    double() #=> 2

::

    def add(a:Int, b:Int) -> Int
      return a + b
    end

    def add(a:Float, b:Float) -> Float
      return a + b
    end

    reduce(add, [1, 2, 3, 4]) #=> 10
    reduce(add, [3.0, 8.2, 7.3]) #=> 18.5
