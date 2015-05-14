.. _jam-methods:

Methods
#######

A method is a scoped group of instructions as a value, that may be executed
given any number of arguments as input and that may output any number of values.
A method may be overloaded with different kinds of inputs or outputs.

The input of a method comes in the form of a collection of variables called
arguments. Input to a method must match exactly one overload.

A method may be defined with a name or anonymously. To overload a method the
same name must be used for each definition in the same scope.

Unlike most other compiled languages, Jam allows you to leave out the type of
arguments. Where no argument type is defined, any parameter with a type that
matches the unspecified type's usage is valid.

At any point in the method a return statement may be made to cause the method
to complete and take the given value as the output of the method call. When
the return value of a method is explicitly defined, all possible execution paths
must return.

Syntax
======

.. productionlist::
    Argument: `Variable` ["=" `Value`]
    Method: [`Visibility`] "def" `Identifier` "(" [ [`Argument` ","]* `Argument` ] ")" [ "->" `Type` ]
          :   (`InstructionSet` | ("return" [`Value`])
          : )* "end"


Examples
--------

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
