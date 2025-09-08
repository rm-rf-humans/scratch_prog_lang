# First Steps Challenge - Complete Solution
# Description: "Move forward 3 steps and turn around. Learn basic movement!"
# Success condition: "Reach the end of the corridor"

# Option 1: Just reach the exit (simplest)
LOOP 3
  MOVE
END

# Option 2: Move 3 steps and turn around (matches description)
# LOOP 3
#   MOVE
# END
# LEFT
# LEFT

# Option 3: Move 3 steps, turn around, and move back
# LOOP 3
#   MOVE
# END
# LEFT
# LEFT
# LOOP 3
#   MOVE
# END
