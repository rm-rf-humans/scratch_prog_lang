# Extension Challenge - Systematic Exploration Algorithm
# This program uses a systematic approach to explore the entire 4x4 room

# Phase 1: Explore all positions systematically
# Start by orienting north
LEFT
LEFT
LEFT
LEFT

# Explore row by row, column by column
# Row 0: Move right across the top
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Turn around and go back
LEFT
LEFT
MOVE
MOVE
MOVE

# Turn right to face south
RIGHT

# Row 1: Move right across second row
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Turn around and go back
LEFT
LEFT
MOVE
MOVE
MOVE

# Turn right to face south
RIGHT

# Row 2: Move right across third row
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Turn around and go back
LEFT
LEFT
MOVE
MOVE
MOVE

# Turn right to face south
RIGHT

# Row 3: Move right across bottom row
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END
MOVE
IF KEY
  PICK
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
END

# Try to find exit
MOVE
IF EXIT
  MOVE
END
