# CHECKLIST: First-Time Build Preparation

Use this checklist to ensure your build environment is properly prepared before starting the Yocto build.

## Pre-Build System Requirements

- [ ] **OS**: Running Linux (Ubuntu 20.04+, Debian 11+, or equivalent)
- [ ] **Disk Space**: At least **50-100 GB free** (check with `df -h`)
  ```bash
  df -h /
  # Look for "Avail" column - should show 50G or more
  ```
- [ ] **RAM**: 8GB+ installed
  ```bash
  free -h
  # Should show 8000M or more available
  ```
- [ ] **CPU Cores**: 4+ (more = faster builds)
  ```bash
  nproc
  ```

## Repository Clone & Setup

- [ ] **Clone with submodules**: 
  ```bash
  git clone --recursive https://github.com/wassimos69/pfe.git
  cd pfe
  ```

- [ ] **Verify submodules are initialized**:
  ```bash
  git submodule status
  # Should show no leading minus signs (✓ = initialized)
  ```

- [ ] **Verify submodule structure**:
  ```bash
  ls -d layers/*/
  # Should list: meta-football, meta-openembedded, meta-raspberrypi, poky
  ```

## System Dependencies Installation

### Ubuntu/Debian Package Check

- [ ] **Build essentials**:
  ```bash
  sudo apt-get install -y build-essential
  gcc --version  # Should be 5.0+
  ```

- [ ] **Required packages**:
  ```bash
  sudo apt-get install -y \
    chrpath diffstat gawk git \
    libfile-copy-recursive-perl liblocale-po-perl \
    libxml-sax-perl python3 python3-pip \
    python3-pexpect python3-jinja2 wget \
    cpio texinfo lz4
  ```

- [ ] **Verify all packages installed**:
  ```bash
  which chrpath git python3 make
  # Should show paths for all commands
  ```

## Python Environment Check

- [ ] **Python 3 version**:
  ```bash
  python3 --version
  # Should be 3.8 or higher
  ```

- [ ] **Required Python modules**:
  ```bash
  python3 -m pip install -q Jinja2 Mako pyyaml
  # or: pip3 install -r requirements.txt
  ```

- [ ] **Verify modules**:
  ```bash
  python3 -c "import jinja2; print('✓ Jinja2')"
  python3 -c "import yaml; print('✓ PyYAML')"
  ```

## BitBake & Poky Setup

- [ ] **BitBake is accessible**:
  ```bash
  export PATH=$(pwd)/layers/poky/bitbake/bin:$PATH
  bitbake --version
  # Should show: BitBake Build Engine, Version X.XX.X
  ```

- [ ] **BitBake can be found after clone**:
  ```bash
  ls layers/poky/bitbake/bin/bitbake
  # Should show the file exists
  ```

## Build Configuration Verification

### build/conf/local.conf

- [ ] **File exists and is readable**:
  ```bash
  cat build/conf/local.conf | head -5
  # Should display configuration without errors
  ```

- [ ] **Critical settings are present**:
  ```bash
  grep "^MACHINE" build/conf/local.conf
  # Should show: MACHINE ??= "raspberrypi5"
  ```

  ```bash
  grep "DISTRO_FEATURES.*systemd" build/conf/local.conf
  # Should show: DISTRO_FEATURES:append = "... systemd ..."
  ```

  ```bash
  grep "VIRTUAL-RUNTIME_init_manager" build/conf/local.conf
  # Should show: VIRTUAL-RUNTIME_init_manager = "systemd"
  ```

- [ ] **File is not corrupted** (has valid syntax):
  ```bash
  bitbake -e | head -10
  # Should work without parse errors (or show parsing messages)
  ```

### build/conf/bblayers.conf

- [ ] **File exists**:
  ```bash
  cat build/conf/bblayers.conf
  ```

- [ ] **All required layers are listed**:
  ```bash
  grep "^BBLAYERS" build/conf/bblayers.conf | grep -q "poky/meta" && echo "✓ poky/meta"
  grep "^BBLAYERS" build/conf/bblayers.conf | grep -q "meta-raspberrypi" && echo "✓ meta-raspberrypi"
  grep "^BBLAYERS" build/conf/bblayers.conf | grep -q "meta-football" && echo "✓ meta-football"
  ```

- [ ] **Layers are in correct order** (meta-football last):
  ```bash
  tail -3 build/conf/bblayers.conf
  # Last line should be: .../layers/meta-football" \
  ```

- [ ] **All layer paths are absolute** (not relative):
  ```bash
  grep -E "(\${|poky|meta-)" build/conf/bblayers.conf
  # Paths should start with / or use ${...}
  ```

## Environment Variables Setup

- [ ] **BUILDDIR set correctly**:
  ```bash
  export BUILDDIR=$(pwd)/build
  echo $BUILDDIR
  # Should show: /path/to/pfe/build
  ```

- [ ] **PATH includes BitBake**:
  ```bash
  export PATH=$(pwd)/layers/poky/bitbake/bin:$PATH
  which bitbake
  # Should show path to bitbake binary
  ```

## Recipe & Layer Verification

- [ ] **meta-football recipes exist**:
  ```bash
  ls layers/meta-football/recipes-*/
  # Should show: connectivity, core, kernel, multimedia
  ```

- [ ] **Custom image recipe exists**:
  ```bash
  ls layers/meta-football/recipes-core/images/rpi5-minimal.bb
  # File should exist
  ```

- [ ] **Camera recipes are available**:
  ```bash
  ls layers/meta-football/recipes-multimedia/
  # Should show directories for libcamera and libpisp
  ```

## Disk Space & Performance

- [ ] **Minimum disk space available**:
  ```bash
  df -BG . | tail -1 | awk '{print $4}'
  # Should show 50+ (gigabytes available)
  ```

- [ ] **No major processes consuming resources**:
  ```bash
  free -h | grep Mem
  # Should show reasonable available memory (not <1GB)
  ```

- [ ] **Build directory is on local disk** (not network):
  ```bash
  df build/
  # Should NOT show nfs, cifs, or remote mount types
  ```

## Documentation & Guides

- [ ] **BUILD_INSTRUCTIONS.md** exists and is readable
- [ ] **README.md** describes the project
- [ ] **VERSIONS.md** documents reproducible versions
- [ ] **MODIFICATIONS.md** explains local customizations

## First Build Test

### Ready to Start?

If all checks pass, you can begin the build:

```bash
# Navigate to build directory
cd build

# Start the build
bitbake rpi5-minimal

# Expected output on successful start:
# Loading cache...
# Loaded X recipes, X skipped, X masked...
# NOTE: Resolving any missing dependencies...
```

### Monitor the Build

In a separate terminal:
```bash
# Watch build progress
tail -f build/bitbake-cookerdaemon.log

# Or use a more detailed monitor
watch -n 5 "ls -lrt build/tmp/work/ | tail -10"
```

## Troubleshooting Checklist Items

### If BitBake doesn't run:
```bash
export PATH=$PATH:$(pwd)/layers/poky/bitbake/bin
bitbake --version
# If still fails, check Python 3 is installed and BitBake files exist
```

### If configuration errors occur:
```bash
cd build
rm -f conf/*.pyc
bitbake -c clean conf/nonexistent 2>&1 | head -20
# Look for parsing errors in bblayers.conf or local.conf
```

### If recipes not found:
```bash
bitbake-layers show-recipes rpi5-minimal
# Should list the recipe and which layer provides it
```

### If layer conflicts:
```bash
bitbake-layers show-overlayed
# Shows which recipes are overridden (should include meta-football)
```

## Success Indicators

After all checks pass, you should see:

1. ✓ No BitBake/configuration errors
2. ✓ All layers listed correctly
3. ✓ rpi5-minimal recipe is found
4. ✓ Disk space monitor shows >50GB available
5. ✓ Build starts and shows "Loading cache..."

---

**If all checks pass, proceed to build**:
```bash
cd build
bitbake rpi5-minimal
```

**Estimated first build time**: 2-3 hours (depending on CPU)

**For issues during build, refer to**:
- `BUILD_INSTRUCTIONS.md` - Full build guide with troubleshooting
- `CORRECTIONS_GUIDE.md` - Common error solutions
- `README_DIAGNOSTIC.md` - Diagnostic procedures
