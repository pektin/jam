while
#####

The ``while`` loop is a special case of ``loop`` that breaks depending on a
condition at the beginning of the loop.

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
