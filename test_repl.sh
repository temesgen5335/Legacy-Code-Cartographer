#!/bin/bash
# Test script for the interactive REPL
# Simulates user commands to verify functionality

echo "Testing Interactive REPL..."
echo ""

# Test commands (each on a new line)
cat << 'EOF' | uv run python cli.py
/help
/list
/whereami
/config_show
/exit
EOF

echo ""
echo "REPL test completed!"
