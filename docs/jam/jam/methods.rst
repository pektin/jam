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

Syntax
======

A method definition starts with the definition keyword (``def``) then with an
optional identifier for the method. Following comes a comma (``,``) separated
list of variable declarations within a pair of brackets (``()``). After that
a newline is expected, followed by any number of instructions and terminated
by the end keyword (``end``).

A method call is similar. It starts with a value equivalent to a method,
followed by a comma (``,``) separated list of values within a pair of brackets
(``()``) that map to a list of variables in one of the methods definitions.

Examples
--------

::

    def double(x)
        return x * 2
    end

    def double()
        return 2
    end

    double(2) #=> 4
    double() #=> 2
