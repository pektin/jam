.. _tut-loop:

loop
####

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
