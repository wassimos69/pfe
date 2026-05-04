#!/bin/bash
# setup.sh - Initialize Yocto build environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POKY_DIR="$SCRIPT_DIR/layers/poky"
BUILD_DIR="$SCRIPT_DIR/build"

echo "================================"
echo "Yocto Build Environment Setup"
echo "================================"

# Check if poky layer exists
if [ ! -d "$POKY_DIR" ]; then
    echo "❌ ERROR: layers/poky not found!"
    echo "   Make sure you cloned with: git clone --recursive https://github.com/wassimos69/pfe.git"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_PYTHON="3.8"
if [ "$(printf '%s\n' "$REQUIRED_PYTHON" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_PYTHON" ]; then
    echo "❌ ERROR: Python 3.8+ required, found: $PYTHON_VERSION"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION found"

# Check for required commands
for cmd in git gcc make chrpath; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ ERROR: $cmd not found. Please install build-essential and dependencies."
        exit 1
    fi
done
echo "✓ Build tools found"

# Add BitBake to PATH
export BUILDDIR=$SCRIPT_DIR/build
export PATH=$POKY_DIR/bitbake/bin:$PATH

# Verify BitBake
if ! bitbake --version > /dev/null 2>&1; then
    echo "❌ ERROR: BitBake not accessible"
    exit 1
fi
BITBAKE_VERSION=$(bitbake --version 2>&1 | head -1)
echo "✓ $BITBAKE_VERSION"

# Verify build/conf exists
if [ ! -f "$BUILD_DIR/conf/local.conf" ]; then
    echo "❌ ERROR: build/conf/local.conf not found"
    exit 1
fi
echo "✓ Build configuration found"

# Display configuration summary
echo ""
echo "================================"
echo "Configuration Summary:"
echo "================================"
echo "Project Directory: $SCRIPT_DIR"
echo "Build Directory: $BUILD_DIR"
echo "Poky Layer: $POKY_DIR"
echo ""
echo "Machine: $(grep '^MACHINE' $BUILD_DIR/conf/local.conf | cut -d'=' -f2 | tr -d ' "')"
echo "Distro: $(grep '^DISTRO' $BUILD_DIR/conf/local.conf | cut -d'=' -f2 | tr -d ' "')"
echo ""

# Source Poky environment
echo "Sourcing Poky environment..."
export BUILDDIR=$SCRIPT_DIR/build
cd $SCRIPT_DIR

# Output shell configuration commands
echo ""
echo "================================"
echo "Environment Ready! Run:"
echo "================================"
echo ""
echo "export BUILDDIR=$SCRIPT_DIR/build"
echo "export PATH=$POKY_DIR/bitbake/bin:\$PATH"
echo "cd build"
echo "bitbake rpi5-minimal"
echo ""
echo "Or use one-liner:"
echo "export BUILDDIR=$SCRIPT_DIR/build && export PATH=$POKY_DIR/bitbake/bin:\$PATH && cd $BUILD_DIR && bitbake rpi5-minimal"
echo ""
