Traits
######

Traits represent a promise of a type. It combines the functionality of an
abstract base class and an interface. A trait may define a set of functions,
with or without implementation, and instance variables.

A class may enforce fulfilment of a trait by inheriting it. By inheriting a
trait, the class mixes in the set of functions and instance variables, while
ensuring unimplemented functions are implemented. Traits may also inherit from
each other in the same way as classes.

Syntax
======

.. productionlist::
    Trait: "trait" `identifier`
         :   `ClassInstructionSet`
         : "end"

Examples
========

::

    trait Person
      name:String

      def new(n)
        name = n
      end
    end

    class Employee : Person
    end

    class Client : Person
    end
