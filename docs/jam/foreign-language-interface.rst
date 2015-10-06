Foreign Language Interface
##########################

Jam supports foreign language interfaces that allow the jam compiler to link
with libraries written in other languages, most notably C. This allows jam users
to reuse code not written in jam.

Because other languages differ so greatly, foreign language interfaces are
supplied per language. The interface may provide any supported jam features that
may be used exactly like natively defined objects.

C Interface
===========

The C interface supports both global variables and functions. Because of C's
static typing every type must be explicitly declared.

Syntax
------

.. productionlist::
    CExtern: "extern" "$C" (`Identifier` `MethodType`) | (`Identifier` ":" `Type`)
