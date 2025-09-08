#!/bin/bash

# One-liner installation for Vault Runner Language Extension
# Usage: curl -fsSL https://raw.githubusercontent.com/rm-rf-humans/scratch_prog_lang/main/scripts/install.sh | bash 

echo " Vault Runner Language Extension - Quick Install "
echo "====================================================="
echo ""
echo "This will install Vault Runner so you can:"
echo "• Write .sc files and execute them like Python"
echo "• Use vault-runner my_program.sc"
echo "• Play the interactive game"
echo "• Try language extensions"
echo ""

# Download and run the main installer
curl -fsSL https://raw.githubusercontent.com/rm-rf-humans/scratch_prog_lang/main/scripts/install.sh | bash

echo ""
echo " Installation complete!"
echo ""
echo " Try it out:"
echo "  echo 'MOVE' > hello.sc"
echo "  vault-runner hello.sc"
echo ""
echo " Other modes:"
echo "  vault-runner -i    # Interactive mode"
echo "  vault-runner -g    # Play the game"
echo "  vault-runner -e    # Try extensions"
echo "  vault-runner -d    # Run demo"
echo ""
echo "Happy programming with Vault Runner! "
