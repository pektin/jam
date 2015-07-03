.. _jam-imports:

Imports
#######

A import allows for the inclusion of objects external to a context inside said
context. Imports follow the same resolution laws as identifiers, but instead of
working from inside their context, they resolve from it's parent.

A import statement also allows for the inclusion of source files outside of the
current file as modules. The resolution path works from the directory of the
source file of the import statement, following the name as directories until one
resolves to a file. The import can also include a ``..`` to indicate a parent
directory. If no source file is found from the relative path, the current
working directory is checked.

A import may also define a specific name which the referenced object will be put
in the local context as. This is useful for avoiding ambiguities, especially for
external packages.

Syntax
------

.. productionlist::
    ImportPath: [ "."+ ] `Identifier` [ "." `Identifier` ]*
    Import: "import" `ImportPath` [ "as" `Identifier` ]
