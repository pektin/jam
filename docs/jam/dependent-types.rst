Dependent Types
###############

A dependent type is a :doc:`type<types>` whose definition depends on its value.
Jam only supports a subset of features usually indicated when referring to
dependent types.

A set of assumptions can be applied to any value in Jam. These assumptions must
hold when using the type. An assumption can be any derivative value that results
in a boolean (such as a method call, or comparison).

Syntax
======

.. productionlist::
    Assertion: "assert" `Value`
    Assumption: "assume" `Value`

Example
-------

::

    def sqrt(x)
      # x >= 0 must be true for this scope
      assume x >= 0

      return # sqrt implementation
    end

    # n doesn't have any assumptions, so it could be anything
    n = input() as Int

    # For sqrt(x), x must be >= 0
    # Type error, n doesn't meet condition: n >= 0
    puts(sqrt(n))

    # Branches on a condition implicitly create assumptions
    if n >= 0
      # Thus this is valid
      puts(sqrt(n))
    else
      puts("n must be >= 0")
    end

    # Jam does not have a deep understanding
    if n < 0
      puts("n is < 0")
    else
      # Type error, n doesn't meet condition n >= 0
      puts(sqrt(n))
    end

    # Can be explicitly overridden, if required
    assume n >= 0
    puts(sqrt(n))

    # Will fail at runtime if assertion is not met
    # Thus it also implicitly creates an assumption
    assert n >= 0
    puts(sqrt(n))
