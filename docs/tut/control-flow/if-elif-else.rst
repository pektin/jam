.. _tut-if-elif-else:

if/elif/else
############

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
