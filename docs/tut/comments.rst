.. _tut-comments:

Comments
########

Jam supports only one kind of comment, which spans for a single line. Since most
modern editors have built-in shortcuts to comment out multiple lines of code,
this is a non-issue.

::

    # Returns the given Fibonacci number
    # Guaranteed to run in constant time
    def fib(n:Int)
        # Formula for finding the nth Fibonacci number
        # Uses the golden ratio constant (Phi) and it's reciprocal (phi)
        const Phi = 1.618_033_988_749_894_848_204_586
        const phi = 1/Phi
        return ((Phi**n - (-phi)**n) / (Phi + phi)) as Int
    end

.. seealso::

    Language reference on :ref:`comments<jam-comments>`
