Control Flow
############

A key part of any programming language is the ability to alter program flow.

if/elif/else
============

Jam supports the standard ``if`` and ``else`` statement, but instead of
``else if``, it uses a condensed ``elif``.

::

    x = 3

    if x > 0
      puts("x is positive")
    elif x < 0
      puts("x is negative")
    else
      puts("x is zero")
    end

loop
====

Jam provides a ``loop`` keyword that describes an infinite loop. All other loop
constructs are built on top of this. Use ``break`` to exit out of the loop.

::

    count = 1
    loop
      puts(count)

      count += 1
      if count > 5
        break
      end
    end

while
=====

The ``while`` loop is a special case of ``loop`` that stops based on a condition
at the beginning of the loop.

::

    while condition
    # is shorthand for
    loop
      if condition
        break
      end

The notorious FizzBuzz program can be written using a while loop.

::

    # Loop from n = 1 to n = 100
    n = 1
    while n <= 100
      if n % 15 == 0
        puts("FizzBuzz")
      elif n % 3 == 0
        puts("Fizz")
      elif n % 5 == 0
        puts("Buzz")
      else
        puts(n)
      end

      n += 1
    end
