# Lekvar

Lekvar is an intermediate representation for Jam. It is designed to be relatively easy to verify, optimise and emit lower level code. In addition to Jam, Lekvar imposes certain restrictions on what is possible to express.

Unlike Jam, Lekvar makes a very clear distinction between variables, functions and types. It is only through clever compiling from Jam to Lekvar that the difference between these structures is abstracted away.

The Lekvar format is generally independent of Jam and similarly to the JVM could be used for languages beyond Jam. Lekvar is highly susceptible to change and currently contains no backward compatibility guarantee, however this will be eventually desirable.

## Design

The design follows similar principles as dynamic programming languages. Every value is an "object" and has a type. Every type is also an object and has a type. As a basis, the only other concept not directly being an object are instructions.

### Objects

In terms of lekvar, every object has a type. An object is seen as a single value to be used in any context where a value is appropriate. An object functions as an abstract base for other language elements.

### Scopes

A scope is a object that fits into a hierarchy of other scopes. Every scope has a collection of named sub-objects and a single parent scope.

### Types

A type is simply a scope, and thereby a object, which holds information about what a certain kind of object can do. A type is a kind of meta-object, if you will. Types can also be compared with each other to check for compatibility. Since a type is also a object, it also has a type itself and can therefore be used as a value. The type of a type is considered a meta-type, which ultimately have the type of `std.Type`.

### Methods

A method is simply a neat wrapping around functions allowing for overloaded argument and return types.

### Functions

A function is an ordered collection of instructions, along with any number of named arguments and return types. A function is more akin to a method in a more traditional sense, but to distinguish between the overloaded and not overloaded kinds these are differentiated in Lekvar.
