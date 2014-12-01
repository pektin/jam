# Lekvar

Lekvar is an intermediate representation for Jam. It is designed to be relatively easy to verify, optimise and emit lower level code. In addition to Jam, Lekvar imposes certain restrictions on what is possible to express.

Unlike Jam, Lekvar makes a very clear distinction between variables, functions and types. It is only through clever compiling from Jam to Lekvar that the difference between these structures is abstracted away.

The Lekvar format is generally independant of Jam and similarly to the JVM could be used for languages beyond Jam. Lekvar is highly succeptable to change and currently contains no backward compatibility guarantee, however this will be eventually desireable.

## Design

The design is primarily based on the current implementation of Lekvar. I'm still in the process of figuring everything out, and as such this section will not be complete for some time.

Visibility of different structures is currently seen as unessecary. This is a feature planned for the future.

### Variables

Variables only have two primary attributes: a name and a type. Typically the type will not be specified and remain `null` until it can be determined. A variable may only have one single type, however this type may change depending on how the variable is used. Variables are only able to be used through references. The only two ways of using a variable is directly as a value, or on the left hand side of an assignment.

When a variable is assigned the type of the assigned value is resolved by recursively resolving the type of the value assigned.  
If an unknown type is resolved, an error is thrown. This can occurr when the variable is assigned to itself for no reason, or assigned to another variable that has yet to be assigned.  
If a temporary type is resolved it is the result of an internal error. All temporary types (templates) are resolvable.  
Otherwise the type of the value is checked with the type of the variable. It is up to the type of type for the action to take with this. This could result in a simple assignment, a check for type casting, or a narrowing down of the possible overloads callable from a function assigned to a variable.

Similar action is taken when a variable is used as a parameter to a function or otherwise.

### References

A reference is literally just a string pointing to a function or variable.
