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
type. As a basis, the only other concept not directly being an object are
instructions.

For debugging and other global input/output, Lekvar creates a `State` object
that is passed from function to function when Lekvar is verified.

### Object

In terms of Lekvar, every object has a type and each objects behaviour is
entirely defined by it's type.

Every object must define:
* `resolveType(Scope, State):Type`, returns the type of the object
* `verify(Scope, State)`, verifies the objects integrity

### Scope

A scope is an Object that also defined a `name:String` and a `parent:Scope`
attribute.

### Type

A type defines what an object is and what it can do. Type is also a Scope.

Every type must define:
* `collectAttributes(State, String):Object`
* `checkCompatibility(Type):Bool`

### Function

A function is a single callable collection of instructions.
