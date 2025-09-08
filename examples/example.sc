# Vault Runner Program Example
# This program demonstrates basic movement and key collection

# Move forward twice
MOVE
MOVE

# Check if there's a key and pick it up
IF KEY
    PICK
END

# Turn left and move
LEFT
MOVE

# Try to open a door if we have a key
IF DOOR
    OPEN
END
