# Scratch Programming Language

A simple programming language for controlling a robot in a 2D vault environment. The robot can navigate through corridors and rooms, pick up keys, open doors, and find exits.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scratch_prog_lang.git

# Install in development mode
cd scratch_prog_lang
pip install -e .
```

## Language Features

The language supports the following commands:
- **Movement**: `MOVE`, `LEFT`, `RIGHT`
- **Actions**: `PICK`, `OPEN`
- **Control Flow**: `LOOP`, `IF`, `WHILE`, `END`
- **Sensors**: `FRONT`, `KEY`, `DOOR`, `EXIT`
- **Flags**: `SET`, `CLR`

## Example Programs

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

## Running Tests

```bash
python -m unittest tests/test.py
```

## Project Structure

```
scratch_prog_lang/
├── src/
│   └── scratch/
│       ├── interpreter.py    # Language interpreter
│       ├── vault_runner.py   # Robot simulation
│       └── programs.py       # Example programs
└── tests/
    └── test.py              # Test suite
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open