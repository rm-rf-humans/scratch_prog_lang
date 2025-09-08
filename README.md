# Vault Runner Programming Language

A simple programming language for controlling a robot in a 2D vault environment. The robot can navigate through corridors and rooms, pick up keys, open doors, and find exits. This project includes an interactive game, language extensions, and comprehensive testing.

##  Features

- **Core Language**: Simple, constraint-based programming language (max 20 distinct tokens)
- **Interactive Game**: Play challenges and learn programming concepts
- **Language Extensions**: Advanced commands for complex scenarios
- **Visual Simulation**: Real-time robot movement visualization
- **Comprehensive Testing**: Full test suite with benchmarks

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scratch_prog_lang.git

# Install in development mode
cd scratch_prog_lang
pip install -e .
```

##  Quick Start

### Run the Interactive Demo
```bash
python -m scratch
```

### Play the Game
```bash
python -m scratch
# Select option 7: Play the Vault Runner Game
```

### Try Extensions
```bash
python -m scratch
# Select option 8: Try Language Extensions
```

##  Language Features

### Core Commands
- **Movement**: `MOVE`, `LEFT`, `RIGHT`, `RTURN`
- **Actions**: `PICK`, `OPEN`
- **Control Flow**: `LOOP <n>`, `IF <sensor>`, `WHILE <sensor>`, `END`
- **Sensors**: `FRONT`, `KEY`, `DOOR`, `EXIT`
- **State Management**: `SET`, `CLR`

### Extended Commands (Optional)
- **Timing**: `WAIT <n>` - Pause execution
- **Navigation**: `MARK`, `GOTO` - Mark and return to positions
- **Sensing**: `SCAN`, `COUNT` - Advanced environment analysis
- **State**: `SAVE`, `LOAD` - Save and restore robot state

##  Example Programs

### Simple Movement
```
MOVE
MOVE
LEFT
MOVE
```

### Corridor Navigation
```
WHILE FRONT
    MOVE
    IF KEY
        PICK
    END
    IF DOOR
        OPEN
    END
END
```

### Advanced Program with Extensions
```
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

##  Game Features

The Vault Runner Game includes:

- **6 Progressive Challenges**: From basic movement to complex multi-key scenarios
- **Scoring System**: Points based on efficiency, simplicity, and success
- **Leaderboard**: Track your best scores
- **Practice Mode**: Test programs without scoring
- **Tutorial**: Learn the language step by step

### Challenge Types
1. **First Steps**: Learn basic movement
2. **Key Collector**: Find and collect keys
3. **Door Master**: Open doors and escape
4. **Room Explorer**: Navigate complex environments
5. **Multi-Key Mystery**: Solve puzzles with multiple keys
6. **Speed Run**: Optimize for efficiency

##  Language Extensions

### Extended Commands
- `WAIT <n>`: Pause execution for n steps
- `MARK`: Mark current position for later reference
- `GOTO`: Move to previously marked position
- `SCAN`: Check all four directions at once
- `COUNT`: Count items in surrounding area
- `SAVE`: Save current robot state
- `LOAD`: Restore previously saved state

### Advanced Features
- **Multiple Keys**: Support for multiple key types
- **Teleportation**: Jump between marked locations
- **Energy System**: Resource management for actions
- **Extended Vision**: See further in all directions
- **State Management**: Save and restore complete robot state

##  Testing

### Run All Tests
```bash
python -m unittest tests/test.py
```

### Run with Benchmarks
```bash
python tests/test.py
```

### Test Coverage
- Unit tests for all core functionality
- Integration tests for complete programs
- Performance benchmarks
- Error handling validation
- Extension compatibility tests

##  Project Structure

```
scratch_prog_lang/
├── src/
│   └── scratch/
│       ├── __init__.py
│       ├── __main__.py          # Main entry point
│       ├── interpreter.py       # Core language interpreter
│       ├── vault_runner.py      # Robot simulation engine
│       ├── programs.py          # Example programs
│       ├── game.py              # Interactive game
│       └── extensions.py        # Language extensions
├── tests/
│   └── test.py                  # Comprehensive test suite
├── docs/                        # Documentation
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

##  Use Cases

### Educational
- Learn programming concepts through visual simulation
- Understand control flow and conditional logic
- Practice algorithm design and optimization

### Research
- Study constraint-based programming languages
- Analyze program complexity and efficiency
- Test different navigation algorithms

### Entertainment
- Solve puzzles and challenges
- Compete for high scores
- Create and share programs

##  Program Analysis

The system provides detailed analysis of programs:

- **Token Count**: Total and distinct token usage
- **Complexity Score**: Algorithmic complexity measurement
- **Control Structures**: Loop and conditional analysis
- **Nesting Depth**: Maximum control structure nesting
- **Extension Usage**: Advanced feature utilization

##  Performance

- **Execution Speed**: Optimized interpreter for real-time simulation
- **Memory Efficiency**: Minimal memory footprint
- **Safety Limits**: Built-in protection against infinite loops
- **Debugging Support**: Step-by-step execution tracking

##  Documentation

- **API Reference**: Complete function and class documentation
- **Tutorial**: Step-by-step learning guide
- **Examples**: Comprehensive program examples
- **Best Practices**: Programming guidelines and tips

##  Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Run linting
python -m flake8 src/

# Run type checking
python -m mypy src/
```

##  License

MIT License - see [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Inspired by educational programming languages
- Built for learning and experimentation
- Designed with simplicity and extensibility in mind