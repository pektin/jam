# Lekvar

Lekvar is an intermediate representation for Jam. It is designed to be
relatively easy to verify, optimise and emit lower level code. In addition to
Jam, Lekvar imposes certain restrictions on what is possible to express.

Unlike Jam, Lekvar makes a very clear distinction between variables, functions
and types. It is only through clever compiling from Jam to Lekvar that the
difference between these structures is abstracted away.

The Lekvar format is generally independent of Jam and similarly to the JVM could
be used for languages beyond Jam. Lekvar is highly susceptible to change and
currently contains no backward compatibility guarantee, however this will be
eventually desirable.

## Builtins

In order for Lekvar to verify, a builtin module must exist that contains
standard functionality. The builtin module is a combination of the backend
builtins, which provide the low-level functionality, and the frontend builtins,
which provide the higher level features for the frontend.

## Design

The design follows similar principles as dynamic programming languages. Every
value is an "object" and has a type. Every type is also an object and has a
type.

### Object

A object represents a singular value. If a object does not have a type, it is
considered a instruction and cannot be used as a value.

### Context

A context is a structure that binds objects to other objects. A context is bound
to a singular scope, a bound object itself, and has a set of objects that are
bound to it's scope.

### Bound Object

A bound object is a object that can both have a context and/or be bound to one.
Since objects are bound by their name, every bound object must have a name.

### Type

A type is an object that holds information on that object. A type may supply a
context for the object or what happens when the object is called. A type itself
is also an object and therefore also has a type. The type of types may not be
cyclic until it reaches the base type, whose type is itself.
