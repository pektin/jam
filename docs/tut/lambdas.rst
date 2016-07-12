Lambdas
#######

Lambdas are similar to methods, except that lambdas are anonymous, ie. they do
not have a name. Lambdas may also only have a single value for execution, ie.
one line, which is automatically returned. Thus they are most similar to
mathematical functions (eg. `f(x) = x^2`).

::

    a = (v) => v**2

    puts(a(2)) # 4

    # is almost the same as

    a = def fn(v)
          return v**2
        end

    puts(a(2))  # 4
    puts(fn(2)) # fn is also defined

Because lambdas do not have a name, they also can't be overloaded like methods.

::

    a = (v) => v**2
    a = (v, w) => v * w # Invalid!

Since lambdas that take one or zero arguments are common, when defining those
one can leave out the `()` brackets.

::

    a = v => v**2
    puts(a(2)) # 4

    b = => a(2)
    puts(b()) # 4

    def do_twice(action)
      action()
      action()
    end
    do_twice(=> puts(2)) # 2
                         # 2
