# Jam Syntax

This file is designed to describe the current ideas surrounding the syntax for Jam. This should be a point of discussion instead of a directive/law. It simply describes the current consensus concerning syntax.

## Overall Idea

The syntax is C based, primarily because the large majority of modern programming languages are also C based. Most text editors also easily support C based languages. There does not seem to be any obvious reason to reinvent the wheel for this one.

## Ideals

Other than it's origins in C, the syntax is designed to follow the following set of ideals:
 - Easy to read / easy on the eyes (after all, we'll end up reading it sooner or later)
 - Uses a small number of concepts that expand out to more powerful compound concepts (ie. Instead of having blocks and functions, just have functions be blocks assigned to a variable. This reduces the complexity of the language and it's syntax)
 - No fluff, where it doesn't contradict readability. (Writing code shouldn't be like writing an essay)
 - Syntax consistent and independent of compiler (If types are CamelCase, don't put `int` into the built-in types. I'm looking at you: Python)
 - Context free grammars. 

## Restrictions

Because of the lekvar implementation and C based nature of Jam, this imposes certain restrictions on the syntax. These restrictions should be consistent with the ideals.

### Variable declaration

Variable assignments have optional type declarations. It's type can either be specified or implied. Since the use of keywords such as `auto` to signify an implied type is fluff there are only two options:
C like:
`<Type> <name>`
or (like some other languages):
`<name> <Type>`

With implied types and without the `auto` keyword, this creates context dependant grammar when keywords are used:

`int foo = 1`
`const foo = 1`

The use of `const` is indistinguishable from the use of `int` in this example. Therefore the only option is having the type declared after the variable's name.
