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

### Object

An object is a singular, local object. The object must have a type. A object is considered an instruction when it's type is `None`.

### Context

A context is a collection of bound objects that is bound to an object. A context can be used to link a scope to it's children, but can also be used for other kinds of contexts. A context may also fake a child, making the connection to the context one way.

### BoundObject

The same as an object, except that this object has to be bound to a context. Every bound object must therefore have a name, and a reference to the context it is bound to.

### Type

A type is an object that is used to describe another object. It provides the attributes and functions of said described object.
