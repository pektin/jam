.. _jam-booleans:

Booleans
########

A boolean represents a value that can only be in two states, either true or
false. Booleans are of the builtin type ``Bool``.

Syntax
======

.. productionlist::
    Booleans: "true" | "false"

Example
-------

::
	# Boolean variables used in a conditional block
	state = true

	if state == true
		print("This will print\n")
	else
		print("This will not\n")
	end


	# Boolean value used in a conditional block 
	if true
		print("This will always print")
	else
		print("This will never print")
	end
