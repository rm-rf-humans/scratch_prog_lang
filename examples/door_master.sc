# Door Master - Corridor Navigation (Program 1)
# Navigate twisting corridor with unknown start position/direction  
# Two-phase strategy: 1) Move to end and get key, 2) Find vertical path
WHILE FRONT
  MOVE
  IF KEY
    PICK
  END
END
LEFT
WHILE FRONT
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
  IF EXIT
    MOVE
  END
END
RIGHT
WHILE FRONT
  MOVE
  IF DOOR
    OPEN
    MOVE
  END
  IF EXIT
    MOVE
  END
END
