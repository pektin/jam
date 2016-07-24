Traits
######

Traits represent a promise of a type. It combines the functionality of an
abstract base class and an interface. A trait may define a set of
:doc:`methods`, with or without implementation, and instance variables.

A class may enforce fulfilment of a trait by inheriting it. By inheriting a
trait, the class mixes in the set of methods and instance variables, while
enforcing unimplemented methods are implemented. Traits may also inherit from
each other in the same way as classes.

Syntax
======

.. note::
    A syntax for undefined methods is yet to be determined

.. productionlist::
    Trait: "trait" `identifier` `ClassInstructionSet` "end"

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
