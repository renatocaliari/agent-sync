#!/bin/bash

# Cleanup duplicate skills from native agents
# Native agents (qwen-code, pi.dev) read from ~/.agents/skills/ directly
# They don't need local copies

echo "🧹 Cleaning up duplicate skills from native agents..."
echo ""

# Check if skills exist in centralized location
if [ ! -d "$HOME/.agents/skills" ]; then
    echo "❌ Error: ~/.agents/skills/ not found"
    echo "   Run 'agent-sync skills centralize' first"
    exit 1
fi

# Count skills in centralized location
CENTRALIZED_COUNT=$(find "$HOME/.agents/skills" -maxdepth 1 -type d -name "*-*" 2>/dev/null | wc -l | tr -d ' ')
echo "📚 Found $CENTRALIZED_COUNT skills in ~/.agents/skills/"
echo ""

# Clean qwen-code
if [ -d "$HOME/.qwen/skills" ]; then
    QWEN_COUNT=$(find "$HOME/.qwen/skills" -maxdepth 1 -type d -name "*-*" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$QWEN_COUNT" -gt 0 ]; then
        echo "🗑  Removing $QWEN_COUNT duplicate skills from qwen-code..."
        rm -rf "$HOME/.qwen/skills"/*
        echo "   ✓ Cleaned ~/.qwen/skills/"
    else
        echo "✓ qwen-code already clean"
    fi
else
    echo "✓ qwen-code has no skills directory"
fi

# Clean pi.dev
if [ -d "$HOME/.pi/agent/skills" ]; then
    PI_COUNT=$(find "$HOME/.pi/agent/skills" -maxdepth 1 -type d -name "*-*" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$PI_COUNT" -gt 0 ]; then
        echo "🗑  Removing $PI_COUNT duplicate skills from pi.dev..."
        rm -rf "$HOME/.pi/agent/skills"/*
        echo "   ✓ Cleaned ~/.pi/agent/skills/"
    else
        echo "✓ pi.dev already clean"
    fi
else
    echo "✓ pi.dev has no skills directory"
fi

echo ""
echo "✨ Cleanup complete!"
echo ""
echo "Native agents will now read skills directly from:"
echo "  ~/.agents/skills/ (single source of truth)"
echo ""
