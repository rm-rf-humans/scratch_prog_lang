# Vault Runner Language Extension

Transform Vault Runner into a command-line programming language that works just like Python!

##  Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/rm-rf-humans/scratch_prog_lang/main/install.sh | bash
```

##  Usage

### Execute .sc files directly:
```bash
vault-runner my_program.sc
vault-runner my_program.sc -v  # Verbose output
```

### Interactive modes:
```bash
vault-runner -i    # Interactive demo
vault-runner -g    # Play the game
vault-runner -e    # Try extensions
vault-runner -d    # Run demo
```

##  Writing Programs

Create a `.sc` file with your Vault Runner program:

```sc
# hello.sc
MOVE
MOVE
IF KEY
    PICK
END
LEFT
MOVE
```

Then execute it:
```bash
vault-runner hello.sc
```

##  Available Commands

### Core Commands
- `MOVE` - Move forward
- `LEFT` - Turn left
- `RIGHT` - Turn right
- `RTURN` - Random turn
- `PICK` - Pick up key
- `OPEN` - Open door
- `LOOP <n>` - Loop n times
- `WHILE <sensor>` - While condition
- `IF <sensor>` - If condition
- `END` - End block
- `SET` - Set flag
- `CLR` - Clear flag

### Sensors
- `FRONT` - Check if front is clear
- `KEY` - Check if on key
- `DOOR` - Check if at door
- `EXIT` - Check if at exit

### Extended Commands (Optional)
- `WAIT <n>` - Wait n steps
- `MARK` - Mark position
- `GOTO` - Go to marked position
- `SCAN` - Scan all directions
- `COUNT` - Count nearby items
- `SAVE` - Save state
- `LOAD` - Load state

##  File Structure

After installation:
```
~/.vault-runner/
├── scratch/           # Core language files
├── tests/            # Test suite
├── example.sc        # Basic example
└── README.md         # Documentation

~/.local/bin/
└── vault-runner      # Executable command
```

##  Examples

### Basic Movement
```sc
# basic.sc
MOVE
MOVE
LEFT
MOVE
```

### Key Collection
```sc
# collect.sc
WHILE FRONT
    MOVE
    IF KEY
        PICK
    END
END
```

### Advanced with Extensions
```sc
# advanced.sc
MARK
MOVE
MOVE
IF KEY
    PICK
    SAVE
END
GOTO
IF DOOR
    OPEN
END
```

##  Game Integration

The extension includes the full Vault Runner game:
```bash
vault-runner -g
```

##  Testing

Run the test suite:
```bash
vault-runner -d  # Demo includes testing
```

##  Program Analysis

Every program execution includes:
- Token count and distinct token usage
- Control structure analysis
- Complexity scoring
- Extension usage (if applicable)

##  Advanced Features

- **Auto-detection**: Automatically uses extended interpreter if extensions are detected
- **Verbose mode**: `-v` flag shows step-by-step execution
- **Multiple modes**: Interactive, game, extensions, demo
- **Error handling**: Clear error messages and debugging info

##  Language Reference

### Syntax Rules
1. One command per line
2. Indentation for nested blocks
3. Comments start with `#`
4. Maximum 20 distinct tokens
5. Case insensitive

### Control Structures
```sc
# Loop
LOOP 5
    MOVE
END

# Conditional
IF KEY
    PICK
END

# While loop
WHILE FRONT
    MOVE
END
```

### Extensions
```sc
# Mark and return
MARK
MOVE
MOVE
GOTO

# State management
SAVE
MOVE
LOAD

# Timing
WAIT 3
MOVE
```

##  License

MIT License - see LICENSE file for details.
