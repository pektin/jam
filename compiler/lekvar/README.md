# Lekvar

Lekvar is an intermediate representation for Jam. It is designed to be relatively easy to verify, optimise and emit lower level code. In addition to Jam, Lekvar imposes certain restrictions on what is possible to express.

Unlike Jam, Lekvar makes a very clear distinction between variables, functions and types. It is only through clever compiling from Jam to Lekvar that the difference between these structures is abstracted away.

The Lekvar format is generally independent of Jam and similarly to the JVM could be used for languages beyond Jam. Lekvar is highly susceptible to change and currently contains no backward compatibility guarantee, however this will be eventually desirable.

## Design

The design follows similar principles as dynamic programming languages. Every value is an "object" and has a type. Every type is also an object and has a type. As a basis, the only other concept not directly being an object are instructions.

### Abstract Base Classes

These are used as the base for all other structures in Lekvar.

#### Objects

In terms of Lekvar, every object has a type. An object is seen as a single value to be used in any context where a value is appropriate. An object functions as an abstract base for other language elements.

#### Scopes

A scope is a object that fits into a hierarchy of other scopes. Every scope has a collection of named sub-objects and a single parent scope.

#### Types

A type is simply a scope, and thereby a object, which holds information about what a certain kind of object can do. A type is a kind of meta-object, if you will. Types can also be compared with each other to check for compatibility. Since a type is also a object, it also has a type itself and can therefore be used as a value. The type of a type is considered a meta-type, which ultimately have the type of `std.Type`.

### Lekvar Classes

### Variable

A variable is a object container for another object in memory. A variable may only have one single type, but any number of values over its lifetime.

### Assignment

An assignment is an object which causes another object to be assigned as a value to a variable.

### Reference

A reference is a object that refers to another object only by name. The type and verification of a reference is simply taken from the referred object. If it is found that no object or multiple different object go by the same name, a ReferenceError is raised.

#### Functions

A function is a scope that contains an ordered collection of instructions, along with any number of named arguments a return type. A function is more akin to a method in a more traditional sense, but to distinguish between the overloaded and not overloaded kinds these are differentiated in Lekvar.

#### FunctionType

A function type is the type of a function. It only contains the signature of the function, ie. a set of arguments and a return type. A function type is only compatible with another function type that has a compatible signature.

### Return

A return is a break point for a function that takes a single object as a return value. This object may only appear inside of functions and can be used to infer the return type of a function.

#### Call

A call is an object which executes an associated object (currently only functions are supported), passing into the execution a set of arguments.

#### Literal

A literal is a pre-defined piece of data with an associated pre-defined type, just like other languages.

#### External Function

A external function is a function whose instructions are not contained within *this* source. Currently this is only used to link to functions in the c-stdlib, but is planned to be used to link to other Lekvar and non-Lekvar libraries.

### Temporary Classes

These classes are only temporary until more of Lekvar is built to replace these.

#### LLVMType

Directly linked to llvm, this type is used to make current emission of llvm-ir easier, but will be replaced by the standard library in the future.
