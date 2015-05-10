.. _jam-templates:

Templates
#########

A template is similar to a type, but instead of defining all behaviour for
instances, templates only describe a subset. Templates are akin to abstract base
classes from other languages, but behave more like interfaces.

Syntax
======

.. productionlist::
    TemplateInclude: "include" `Template`
    Template: "template" `identifier`
            :     `ClassInstructionSet`
            : "end"

Examples
--------

::

    template Person
      name:String

      def new(n)
        name = n
      end
    end

    class Employee
      include Person
    end

    class Client
      include Person
    end
