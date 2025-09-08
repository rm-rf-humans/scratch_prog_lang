# Example: Move 3 steps forward using LOOP
# This program demonstrates how to use LOOP to repeat MOVE commands

LOOP 3
  MOVE
END

# Alternative: Move 3 steps with safety check
# LOOP 3
#   IF FRONT
#     MOVE
#   END
# END
