Pragma
######

Pragma is a modifier that enforces that its value must be evaluated at compile
time. This is designed to be used as a guarantee that CTFE (Compile Time
Function Evaluation) and constant folding are used as an optimisation for a
particular value.

Syntax
======

.. productionlist::
    Pragma: "pragma" `ModifierValue`

Example
-------
::

    # Enforces that `Kind` is evaluated at compile time
    def spawn(pragma Kind, position:Vec2)
      object = Kind()
      object.position = position
      return object
    end

    new_enemy = spawn(Enemy, Vec2(2, 1)) # `Enemy` is a constant, so this is valid

    # `EnemyKind` is not known at compile time
    EnemyKind = read("enemy.txt").constantize
    # This fails
    new_enemy = spawn(EnemyKind, Vec2(2, 1))

    # Force evaluation of `read` at compile time
    enemy_kind = pragma read("enemy.txt")
    # `EnemyKind` is known at compile time
    EnemyKind = enemy_kind.constantize
    # This succeeds
    new_enemy = spawn(EnemyKind, Vec2(2, 1))
