.. _jam-unittests:

Unittests
#########

Unittests provide a builtin testing framework. The framework consists of
individual, optionally named tests. Each test acts as a global method, but may
be defined anywhere.

Syntax
======

.. productionlist::
    Unittest: "unittest" [ `String` ]
            :     `InstructionSet`
            : "end"

