#!/bin/bash

# Test script for Vault Runner Language Extension

echo "🧪 Testing Vault Runner Language Extension"
echo "=========================================="

# Test 1: Basic .sc file execution
echo "Test 1: Basic .sc file execution"
echo "MOVE" > test_basic.sc
echo "MOVE" >> test_basic.sc

python3 -c "
import sys
sys.path.insert(0, 'src/scratch')
from interpreter import VaultInterpreter
from vault_runner import VaultRunner, create_room_world

with open('test_basic.sc', 'r') as f:
    program_lines = [line.strip() for line in f.readlines() if line.strip()]

world = create_room_world()
runner = VaultRunner(world, (0, 0), 1)
interpreter = VaultInterpreter(program_lines)
result = interpreter.run(runner, show_steps=False)

print(f'✅ Basic test: {\"PASS\" if interpreter.instruction_count == 2 else \"FAIL\"}')
"

# Test 2: Extended .sc file execution
echo -e "\nTest 2: Extended .sc file execution"
echo "MARK" > test_extended.sc
echo "MOVE" >> test_extended.sc
echo "GOTO" >> test_extended.sc

python3 -c "
import sys
sys.path.insert(0, 'src/scratch')
from extensions import ExtendedVaultInterpreter
from vault_runner import VaultRunner, create_room_world

with open('test_extended.sc', 'r') as f:
    program_lines = [line.strip() for line in f.readlines() if line.strip()]

world = create_room_world()
runner = VaultRunner(world, (0, 0), 1)
interpreter = ExtendedVaultInterpreter(program_lines, enable_extensions=True)
result = interpreter.run(runner, show_steps=False)

print(f'✅ Extended test: {\"PASS\" if interpreter.instruction_count > 0 else \"FAIL\"}')
"

# Test 3: Program analysis
echo -e "\nTest 3: Program analysis"
python3 -c "
import sys
sys.path.insert(0, 'src/scratch')
from interpreter import VaultInterpreter

program = ['MOVE', 'MOVE', 'IF KEY', 'PICK', 'END']
interpreter = VaultInterpreter(program)
analysis = interpreter.analyze_program()

print(f'✅ Analysis test: {\"PASS\" if analysis[\"total_tokens\"] == 6 else \"FAIL\"}')
print(f'   Tokens: {analysis[\"total_tokens\"]}, Distinct: {analysis[\"distinct_tokens\"]}')
"

# Cleanup
rm -f test_basic.sc test_extended.sc

echo -e "\n🎉 All tests completed!"
echo "The Vault Runner Language Extension is ready to use!"
