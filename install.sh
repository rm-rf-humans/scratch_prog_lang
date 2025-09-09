#!/bin/bash

# Vault Runner Language - Universal Installer
# This script can be run from anywhere to install Vault Runner

set -e

echo "Vault Runner Language - Universal Installer"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

echo -e "${GREEN}Python 3 found: $(python3 --version)${NC}"

# Check for required tools
if ! command -v curl &> /dev/null && ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Either curl or git is required for downloading.${NC}"
    echo "Please install curl or git and try again."
    exit 1
fi

if ! command -v git &> /dev/null && ! command -v unzip &> /dev/null; then
    echo -e "${RED}ERROR: unzip is required for downloading without git.${NC}"
    echo "Please install unzip and try again."
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/.vault-runner"
BIN_DIR="$HOME/.local/bin"

echo -e "${BLUE}Creating installation directory: $INSTALL_DIR${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Download and install the Vault Runner package
echo -e "${BLUE}Downloading Vault Runner from GitHub...${NC}"

# Create temporary directory for download
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download the repository
if command -v git &> /dev/null; then
    echo -e "${BLUE}Cloning repository with git...${NC}"
    git clone https://github.com/rm-rf-humans/scratch_prog_lang.git vault-runner
else
    echo -e "${BLUE}Downloading with curl...${NC}"
    # Download as zip and extract
    curl -L -o vault-runner.zip https://github.com/rm-rf-humans/scratch_prog_lang/archive/refs/heads/main.zip
    unzip -q vault-runner.zip
    mv scratch_prog_lang-main vault-runner
fi

# Copy the source files to installation directory
if [ -d "vault-runner/src/scratch" ]; then
    echo -e "${BLUE}Copying source files...${NC}"
    cp -r vault-runner/src/scratch "$INSTALL_DIR/"
    [ -d vault-runner/tests ] && cp -r vault-runner/tests "$INSTALL_DIR/" || true
    [ -f vault-runner/pyproject.toml ] && cp vault-runner/pyproject.toml "$INSTALL_DIR/" || true
    [ -f vault-runner/README.md ] && cp vault-runner/README.md "$INSTALL_DIR/" || true
    if [ -d vault-runner/examples ]; then
        cp -r vault-runner/examples "$INSTALL_DIR/"
    fi
    if [ -d vault-runner/docs ]; then
        cp -r vault-runner/docs "$INSTALL_DIR/"
    fi
else
    echo -e "${RED}Failed to download source files from GitHub.${NC}"
    echo -e "${RED}Please check your internet connection and try again.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# Create the vault-runner executable
echo -e "${BLUE}Creating vault-runner executable...${NC}"
cat > "$BIN_DIR/vault-runner" << 'EOF'
#!/usr/bin/env python3
"""
Vault Runner Language Extension
Execute .sc files directly like Python
"""

import sys
import os
import argparse
from pathlib import Path

# Add the installation directory to Python path
INSTALL_DIR = os.path.expanduser("~/.vault-runner")
sys.path.insert(0, os.path.join(INSTALL_DIR, "scratch"))

# Import after setting up the path
try:
    from interpreter import VaultInterpreter
    from vault_runner import VaultRunner, create_corridor_world, create_room_world, create_multi_key_world
    from extensions import ExtendedVaultInterpreter, LanguageExtensions
    from game import VaultRunnerGame
except ImportError as e:
    print(f"Error importing Vault Runner modules: {e}")
    print("Please ensure Vault Runner is properly installed.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Vault Runner Language Extension",
        prog="vault-runner"
    )
    
    parser.add_argument(
        "file", 
        nargs="?", 
        help="Vault Runner program file (.sc) to execute"
    )
    
    parser.add_argument(
        "-i", "--interactive", 
        action="store_true", 
        help="Start interactive mode"
    )
    
    parser.add_argument(
        "-g", "--game", 
        action="store_true", 
        help="Start the Vault Runner game"
    )
    
    parser.add_argument(
        "-e", "--extensions", 
        action="store_true", 
        help="Try language extensions"
    )
    
    parser.add_argument(
        "-d", "--demo", 
        action="store_true", 
        help="Run feature demonstration"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Show detailed execution steps"
    )

    parser.add_argument(
        "-m", "--map",
        choices=["corridor", "room", "multi"],
        default="room",
        help="Select world: corridor | room | multi (default: room)"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="Vault Runner Language Extension v0.2.0"
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.interactive:
        import subprocess
        subprocess.run([sys.executable, os.path.join(INSTALL_DIR, "scratch", "__main__.py")])
    elif args.game:
        game = VaultRunnerGame()
        game.start_game()
    elif args.extensions:
        import subprocess
        subprocess.run([sys.executable, os.path.join(INSTALL_DIR, "scratch", "__main__.py"), "8"])
    elif args.demo:
        import subprocess
        demo_path = os.path.join(INSTALL_DIR, "examples", "demo.py")
        if os.path.exists(demo_path):
            subprocess.run([sys.executable, demo_path])
        else:
            print("Demo not available (examples/demo.py not found)")
    elif args.file:
        execute_sc_file(args.file, args.verbose, args.map)
    else:
        # Default: show help
        parser.print_help()
        print("\nQuick Start:")
        print("  vault-runner -i                            # Interactive mode")
        print("  vault-runner -g                            # Play the game")
        print("  vault-runner -e                            # Try extensions")
        print("  vault-runner -d                            # Run demo")
        print("  vault-runner program.sc                    # Execute .sc (room)")
        print("  vault-runner program.sc -m corridor        # Use corridor map")
        print("  vault-runner program.sc -m multi           # Use multi-key map")

def execute_sc_file(filename, verbose=False, map_name="room"):
    """Execute a .sc file."""
    if not filename.endswith('.sc'):
        print(f"Error: File must have .sc extension")
        sys.exit(1)
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    print(f"Executing Vault Runner program: {filename}")
    print("=" * 50)
    
    try:
        # Read the program
        with open(filename, 'r') as f:
            program_lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if not program_lines:
            print("Error: Program file is empty")
            sys.exit(1)
        
        # Check if program uses extensions
        uses_extensions = any(token in ['WAIT', 'MARK', 'GOTO', 'SCAN', 'COUNT', 'SAVE', 'LOAD'] 
                            for line in program_lines 
                            for token in line.split())
        
        # Create interpreter
        if uses_extensions:
            print("Using extended interpreter (extensions detected)")
            interpreter = ExtendedVaultInterpreter(program_lines, enable_extensions=True)
        else:
            interpreter = VaultInterpreter(program_lines)
        
        # Analyze program
        analysis = interpreter.analyze_program()
        print(f"Program Analysis:")
        print(f"  Total tokens: {analysis['total_tokens']}")
        print(f"  Distinct tokens: {analysis['distinct_tokens']}/20")
        print(f"  Control structures: {analysis['control_structures']}")
        if uses_extensions:
            ext_analysis = LanguageExtensions.analyze_program_complexity(program_lines)
            print(f"  Extensions used: {ext_analysis.get('extension_count', 0)}")
        
        # Create world and runner
        if map_name == "corridor":
            world = create_corridor_world()
            start_pos, start_dir = (0, 0), 1  # East
        elif map_name == "multi":
            world = create_multi_key_world()
            start_pos, start_dir = (4, 3), 0  # North
        else:
            world = create_room_world()
            start_pos, start_dir = (0, 0), 1  # East
        runner = VaultRunner(world, start_pos, start_dir)
        
        print(f"\nInitial world state:")
        runner.display_world()
        
        # Execute program
        print(f"\nExecuting program...")
        result = interpreter.run(runner, show_steps=verbose)
        
        print(f"\nResults:")
        print(f"  Success: {'YES' if result else 'NO'}")
        print(f"  Instructions executed: {interpreter.instruction_count}")
        print(f"  Final position: ({runner.x}, {runner.y})")
        print(f"  Has key: {runner.has_key}")
        print(f"  Door opened: {runner.door_opened}")
        
        if verbose:
            print(f"\nFinal world state:")
            runner.display_world()
        
    except Exception as e:
        print(f"Error executing program: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Make the executable
chmod +x "$BIN_DIR/vault-runner"

# Create a simple .sc file template
echo -e "${BLUE}Creating example .sc file...${NC}"
cat > "$INSTALL_DIR/example.sc" << 'EOF'
# Vault Runner Program Example
# This is a simple program that moves forward and picks up a key

MOVE
MOVE
IF KEY
    PICK
END
LEFT
MOVE
EOF

# Add to PATH if not already there
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}Adding $BIN_DIR to PATH...${NC}"
    
    # Detect shell and add to appropriate profile
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    echo "" >> "$SHELL_RC"
    echo "# Vault Runner Language Extension" >> "$SHELL_RC"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
    
    echo -e "${YELLOW}Added to $SHELL_RC${NC}"
    echo -e "${YELLOW}Please run: source $SHELL_RC${NC}"
    echo -e "${YELLOW}Or restart your terminal${NC}"
fi

echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo -e "${BLUE}What's installed:${NC}"
echo "  - vault-runner command in $BIN_DIR"
echo "  - Vault Runner source files in $INSTALL_DIR"
echo "  - Example program: $INSTALL_DIR/example.sc"
echo ""
echo -e "${BLUE}Usage examples:${NC}"
echo "  vault-runner -i                            # Interactive mode"
echo "  vault-runner -g                            # Play the game"
echo "  vault-runner -e                            # Try extensions"
echo "  vault-runner -d                            # Run demo"
echo "  vault-runner example.sc                    # Execute .sc file (room)"
echo "  vault-runner my_program.sc -m corridor     # Execute on corridor map"
echo "  vault-runner my_program.sc -m multi        # Execute on multi-key map"
echo ""
echo -e "${BLUE}Create your first program:${NC}"
echo "  echo 'MOVE' > hello.sc"
echo "  vault-runner hello.sc"
echo ""
echo -e "${GREEN}Happy programming with Vault Runner!${NC}"
