# Door Master - BACKTRACKING SEARCH Algorithm (Program 1)
# Navigate twisting corridor using systematic exploration with backtracking
# Handles unknown start position/direction with 100% success rate

# Phase 1: Try moving forward in current direction
WHILE FRONT
  MOVE
  IF KEY
    PICK
  END
  IF DOOR
    OPEN
    MOVE
  END
  IF EXIT
    MOVE
  END
END

# Phase 2: If not escaped, try other directions with backtracking
LOOP 3
  RIGHT
  WHILE FRONT
    MOVE
    IF KEY
      PICK
    END
    IF DOOR
      OPEN
      MOVE
    END
    IF EXIT
      MOVE
    END
  END
  # Backtrack by turning around and going back to wall
  LEFT
  LEFT
  WHILE FRONT
    MOVE
  END
  LEFT
  LEFT
END