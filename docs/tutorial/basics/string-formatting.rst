.. _tutorial-basics-string-formatting:

String Formatting
#################

.. todo::
    Introduce strings

The following control characters are supported.

======== ============================
Sequence Meaning
======== ============================
``\"``   Literal double quote (``"``)
``\\``   Literal backslash (``\``)
``\0``   Binary zero
``\a``   BEL character
``\b``   Backspace
``\f``   Formfeed
``\n``   Newlines
``\r``   Carriage return
``\t``   Horizontal Tab
``\v``   Vertical Tab
======== ============================

String interpolation is also supported through the use of a hashtag and open
curlybrace (``#{``), followed by any value and a closing curlybrace (``}``).

::

    name = "Harold"

    # This function will print out "My name is Harrold"
    puts("My name is #{name}")

In contrast WYSIWYG strings start and end with backticks (`````) and have no
special formatting.

::

    # This will print "Hello World" with a newline
    puts(`Hello World`)


See more
========
:ref:`Strings language reference<jam-literals-strings>`
