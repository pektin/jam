Methods
#######

In order to separate program logic and allow reuse, code can be grouped together
inside a method. In order to run the code defined inside a method, the method
must be 'called'.

::

    def introduction()
      puts("Hello!")
      puts("I am Jam")
    end

    introduction()

A method may define a set of variables, called arguments, that must be given as
an input to the method when called. Like any other variable, the type of an
argument may be left out.

.. note::

    ``puts`` is also a method, part of a whole set of methods predefined by the
    language.

::

    def say_hello_to(name)
      puts("Hello, #{name}!")
    end

    say_hello_to("John")
    say_hello_to("World")

A method may also return a set of values that can then be used by the caller.
The type of the return value may be explicitly stated.

::

    # Calculates the length of a hypotenuse,
    # given the lengths of the other two sides of a right-angled triangle.
    def pythag_hypotenuse(a:Real, b:Real) -> Real
      # The sqrt function returns the square root of its argument.
      return sqrt(a**2 + b**2)
    end

    a = pythag_hypotenuse(12.3, 8.3)

Methods may be 'overloaded' with different arguments/argument types. This
concept should be used sparingly, but avoids unnecessary name clutter (ie.
``printf``, ``fprintf``, ``sprintf`` and ``snprintf`` from C)

::

    def say_hello_to(name:String)
      puts("Hello, #{name}!")
    end

    def say_hello_to(number:Int)
      say_hello_to("number #{number}")
    end

    say_hello_to("Bob") # Hello, Bob
    say_hello_to(12)    # Hello, number 12

A method call must always match exactly one overload. Matching more than one
means ambiguity, which results in a compiler error.

::

    def not_right(number:Int)
      puts(number)
    end

    def not_right(number:Int)
      not_right(number + 12)
    end

    # The compiler can't know which one to execute, so it errs
    not_right(4)

Methods whose arguments do not have a defined type are considered to be more
generic than those that do. Because of this, the non-generic methods are checked
for matching overloads separately and before the generic ones are. This allows
for specialisation.

::

    # A generic implementation
    def pythag_hypotenuse(a, b)
      return sqrt(a**2 + b**2)
    end

    # Specialisation for integers
    def pythag_hypotenuse(a:Int, b:Int)
      # Actually perform the calculation with reals and convert back to integers after.
      result = pythag_hypotenuse(a as Real, b as Real)
      return result as Int
    end

    pythag_hypotenuse(12.3, 5.4) # Uses the generic implementation
    pythag_hypotenuse(5, 8.3) # Uses the generic implementation
    pythag_hypotenuse(5, 2) # Uses the specialisation for integers

Methods can also be used as values themselves, in the same exact way as any
other value. This works together with overloads and specialisation.

::

    def do_twice(action)
      action()
      action()
    end

    def say_hello()
      puts("Hello")
    end

    do_twice(lazy say_hello)
