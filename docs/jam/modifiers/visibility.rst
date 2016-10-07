Visibility
##########

Visibility modifiers restrict how a statically available object can be accessed
outside of its scope. Visibility can exclusively be "public", "private" or
"protected" and is defaulted to "public".

Syntax
======

.. productionlist::
    VisibilityModifiers: "public" | "private" | "protected"
    Visibility: `VisibilityModifiers` `ModifierValue`
