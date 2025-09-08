# Extension Challenge Example Program
# This program demonstrates how to solve the extension challenge:
# - Multiple keys exist, but only one opens the door
# - Unknown starting position and direction
# - Must find the correct key and escape

# Strategy: Explore systematically and try each key
# 1. Move in a pattern to explore the room
# 2. When we find a key, pick it up
# 3. Try to open the door
# 4. If door doesn't open, continue exploring

# Start by turning to face a known direction (North)
LEFT
LEFT
LEFT
LEFT

# Explore the room systematically
# Move forward and check for key
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Turn right and continue exploring
RIGHT
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Turn right and continue
RIGHT
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Turn right and continue
RIGHT
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# If we haven't escaped yet, try moving to exit
MOVE
IF EXIT
  MOVE
END
