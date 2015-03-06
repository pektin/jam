# Lekvar

Lekvar is an intermediate representation for Jam. It is designed to be relatively easy to verify, optimise and emit lower level code. In addition to Jam, Lekvar imposes certain restrictions on what is possible to express.

Unlike Jam, Lekvar makes a very clear distinction between variables, functions and types. It is only through clever compiling from Jam to Lekvar that the difference between these structures is abstracted away.

The Lekvar format is generally independent of Jam and similarly to the JVM could be used for languages beyond Jam. Lekvar is highly susceptible to change and currently contains no backward compatibility guarantee, however this will be eventually desirable.

## Builtins

In order for Lekvar to verify, a builtin module must exist that contains standard functionality. The builtin module is a combination of the backend builtins, which provide the low-level functionality, and the frontend builtins, which provide the higher level features for the frontend.

## Design

The design follows similar principles as dynamic programming languages. Every value is an "object" and has a type. Every type is also an object and has a type. As a basis, the only other concept not directly being an object are instructions.

### Object

In terms of Lekvar, every object has a type and each objects behaviour is entirely defined by it's type.

Every object must define:
* `resolveType(Scope):Type`, returns the type of the object
* `verify(Scope)`, verifies the objects integrity
* `collectReferences(Scope, String):Object`, returns possible attributes of the object

### Type

A type defines what an object is and what it can do. Type is also an Object.

Every type must define:
* `collectAttributes(String)`
