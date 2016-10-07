Pragma
######

Pragma is a modifier that enforces that its value must be evaluated at compile
time. This is designed to be used as a guarantee that something is evaluated at
compile time, such as calculating a complicated constant, reading a file or even
testing.

Syntax
======

.. productionlist::
    Pragma: "pragma" `ModifierValue`

Examples
--------
::

    fibonacci_cache = [1, 1]

    # Pre-fill fibonacci_cache with the first 200 values
    pragma build_fibonacci_cache(200)

    def build_fibonacci_cache(n:Int)
      i = 0
      while i < n
        # fibonacci auto-fills the cache
        fibonacci(i)
        i += 1
      end
    end

    # Naive cached fibonacci implementation
    def fibonacci(n:Int)
      if n < fibonacci_cache.length
        return fibonacci_cache[n]
      else
        value = fibonacci(n - 1) + fibonacci(n - 2)
        fibonacci_cache[n] = value
        return value
      end
    end

::

    # Read a file at compile time
    constants = pragma read("player_constants.txt").lines

    const MAX_HEALTH = constants[0]
    const MAX_ARMOUR = constants[1]
    const MAX_SPEED  = constants[1]
