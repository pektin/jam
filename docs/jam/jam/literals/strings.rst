.. _jam-literals-strings:

Strings
#######

A string is a sequence of byte data representing characters of a certain format.
There are two different types of strings, ones which allow special characters
and string interpolation and ones which have no special formatting. These are
called format and wysiwyg strings respectively. All strings are of the builtin
type ``String``.

Syntax
======

Format strings start and end with double quotes (``"``) and may contain any of
the following escape sequences:

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

Format strings also support string interpolation. String interpolation starts
with a hashtag and open curlybrace (``#{``), followed by any value and ends with
a closing curlybrace (``}``).

Wysiwyg strings start and end with backticks (`````) and have no special
formatting.

Examples
--------

::

    "Foo: \"#{foo}\""
    `\"\f`
