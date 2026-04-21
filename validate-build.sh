#!/bin/bash

# Validation script - Ensure all prerequisites are met before building

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

echo "=================================="
echo "Yocto Build Environment Validation"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.8.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    pass "Python $python_version (required: $required_version+)"
else
    fail "Python $python_version is too old (required: $required_version+)"
fi

# 2. Check required system packages
echo ""
echo "2. Checking required system packages..."
required_commands=(
    "git:git"
    "make:make"
    "gcc:gcc"
    "wget:wget"
    "diffstat:diffstat"
    "chrpath:chrpath"
)

for cmd_spec in "${required_commands[@]}"; do
    cmd_name="${cmd_spec%%:*}"
    cmd_binary="${cmd_spec##*:}"
    if command -v "$cmd_binary" &> /dev/null; then
        pass "$cmd_name installed"
    else
        fail "$cmd_name not installed - run: sudo apt-get install $cmd_name"
    fi
done

# 3. Check required Python packages
echo ""
echo "3. Checking Python dependencies..."
python_packages=(
    "jinja2"
    "mako"
    "pyyaml"
)

for pkg in "${python_packages[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        pass "Python package: $pkg"
    else
        warn "Python package missing: $pkg - run: pip3 install -r requirements.txt"
    fi
done

# 4. Check repository structure
echo ""
echo "4. Checking repository structure..."

# Check main directories
dirs_to_check=("layers" "build/conf" "layers/meta-football")
for dir in "${dirs_to_check[@]}"; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        pass "Directory exists: $dir"
    else
        fail "Directory missing: $dir"
    fi
done

# 5. Check submodules
echo ""
echo "5. Checking Yocto layers (submodules)..."

submodules=("poky" "meta-raspberrypi" "meta-openembedded" "meta-football")
for layer in "${submodules[@]}"; do
    layer_path="$REPO_ROOT/layers/$layer"
    
    if [ -d "$layer_path" ]; then
        # Check if not empty
        if [ "$(ls -A "$layer_path" 2>/dev/null)" ]; then
            pass "Layer present: $layer"
        else
            fail "Layer empty (not initialized): $layer"
        fi
    else
        fail "Layer missing: $layer"
    fi
done

# 6. Check critical build configuration files
echo ""
echo "6. Checking build configuration..."

config_files=(
    "build/conf/local.conf"
    "build/conf/bblayers.conf"
)

for config in "${config_files[@]}"; do
    if [ -f "$REPO_ROOT/$config" ]; then
        pass "Config file exists: $config"
    else
        fail "Config file missing: $config - run: source poky/oe-init-build-env build"
    fi
done

# 7. Verify critical settings in local.conf
echo ""
echo "7. Verifying critical build settings..."

if grep -q "^MACHINE = \"raspberrypi5\"" "$REPO_ROOT/build/conf/local.conf"; then
    pass "MACHINE is set to raspberrypi5"
else
    fail "MACHINE not set to raspberrypi5 in build/conf/local.conf"
fi

if grep -q "^INIT_MANAGER = \"systemd\"" "$REPO_ROOT/build/conf/local.conf"; then
    pass "INIT_MANAGER is set to systemd"
else
    warn "INIT_MANAGER not set to systemd (may use default sysvinit)"
fi

if grep -q "^LIBC = \"musl\"" "$REPO_ROOT/build/conf/local.conf"; then
    pass "LIBC is set to musl"
else
    warn "LIBC not set to musl (using default glibc)"
fi

# 8. Verify layers in bblayers.conf
echo ""
echo "8. Verifying layers in bblayers.conf..."

required_layers=("meta-football" "meta-raspberrypi" "meta-openembedded")
for layer in "${required_layers[@]}"; do
    if grep -q "$layer" "$REPO_ROOT/build/conf/bblayers.conf"; then
        pass "Layer configured: $layer"
    else
        fail "Layer not in bblayers.conf: $layer"
    fi
done

# 9. Check disk space
echo ""
echo "9. Checking available disk space..."

available_space=$(df "$REPO_ROOT" | awk 'NR==2 {print $4}')
available_gb=$((available_space / 1024 / 1024))

if [ $available_gb -ge 100 ]; then
    pass "Disk space: ${available_gb}GB available (recommended: 100GB+)"
elif [ $available_gb -ge 50 ]; then
    warn "Disk space: ${available_gb}GB available (minimum: 50GB, recommended: 100GB+)"
else
    fail "Insufficient disk space: ${available_gb}GB (need at least 50GB)"
fi

# 10. Check RAM
echo ""
echo "10. Checking available RAM..."

available_ram=$(free -m | awk 'NR==2 {print $7}')

if [ $available_ram -ge 4000 ]; then
    pass "Available RAM: ${available_ram}MB (recommended: 8GB+)"
elif [ $available_ram -ge 2000 ]; then
    warn "Available RAM: ${available_ram}MB (minimum: 4GB, recommended: 8GB+)"
else
    fail "Insufficient RAM: ${available_ram}MB (need at least 2GB)"
fi

# Summary
echo ""
echo "=================================="
echo -e "${GREEN}✓ All validations passed!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. cd $REPO_ROOT"
echo "2. source poky/oe-init-build-env build"
echo "3. bitbake rpi5-minimal"
echo ""
echo "Build time: ~30-90 minutes (first build)"
echo "Result: build/tmp/deploy/images/raspberrypi5/core-image-minimal-*.wic.gz"
echo ""
