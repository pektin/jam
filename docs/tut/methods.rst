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

::

    # Calculates the length of a hypotenuse,
    # given the lengths of the other two sides of a right-angled triangle.
    def pythag_hypotenuse(a:Real, b:Real)
        # The sqrt function returns the square root of its argument.
      return sqrt(a**2 + b**2)
    end
