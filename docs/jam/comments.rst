Comments
########

Comments allow the programmer to add metadata to code in the form of natural
language. They allow a programmer to add descriptions otherwise impossible to
add with standard code for themselves or others. It is advised to use comments
in order to keep code maintainable, avoiding any duplicate descriptions between
the code and the comments.

Multi-line comments do not exist, primarily because most modern code editing
tools have shortcuts to achieve the same thing with single line comments.

Syntax
======

.. productionlist::
    Comment: "#" .* \n

Examples
========
::

    # Find the distance using pythag
    dist = (x**2 + y**2)**0.5

    const phi = 1.618 # golden ratio

    # Perform dijkstra's algorithm on a graph, from a source
    # Uses a fibonacci heap, thereby running in O(E + V log V)
    def dijkstra(graph, source)
      # TODO: Implement
    end
