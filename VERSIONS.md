# Build Reproducibility - Version Information

## Purpose
This document ensures that anyone building this project gets the exact same image output. All versions are pinned at specific commits.

## Layer Versions (Pinned Commits)

Check current pinned versions with:
```bash
cd /path/to/pfe
git submodule status
```

Expected output format:
```
[COMMIT_HASH] layers/meta-football (description)
[COMMIT_HASH] layers/meta-openembedded (description)
[COMMIT_HASH] layers/meta-raspberrypi (description)
[COMMIT_HASH] layers/poky (description)
```

### Layer Details

#### 1. Poky (Yocto Core)
- **Branch**: scarthgap (stable)
- **Release**: 5.0.16 (LTS-equivalent)
- **URL**: https://git.yoctoproject.org/git/poky.git
- **Purpose**: Core Yocto build system, BitBake, base recipes
- **Update Frequency**: Rarely (pin to major releases)

#### 2. Meta-RaspberryPi (Board Support Package)
- **Branch**: scarthgap (matches Poky)
- **URL**: https://github.com/yoctoproject/meta-raspberrypi.git
- **Purpose**: Raspberry Pi 5 hardware support, device tree, kernel
- **Key Recipes**:
  - `linux-raspberrypi` (kernel)
  - `rpi-bootfiles` (bootloader)
  - libcamera support
- **Note**: This repo has **MODIFICATIONS** in our branch (camera/WiFi enhancements)

#### 3. Meta-OpenEmbedded (Community Recipes)
- **Branch**: scarthgap
- **URL**: https://github.com/openembedded/meta-openembedded.git
- **Components Used**:
  - `meta-oe` - General recipes (base system utilities)
  - `meta-multimedia` - Multimedia libraries (libcamera, ffmpeg, etc.)
- **Purpose**: Extended recipe library beyond Poky

#### 4. Meta-Football (Our Custom Layer)
- **Location**: `layers/meta-football/`
- **Version Control**: Git submodule (this repo)
- **Branch**: main
- **Recipes**:
  - WiFi auto-connection (wpa-supplicant, wifi-busybox)
  - Camera module support
  - Kernel configuration overrides
  - Root filesystem initialization

## Build Tool Versions

### Required Software Versions

| Tool | Minimum Version | Tested Version | Notes |
|------|-----------------|-----------------|-------|
| Python | 3.8 | 3.10, 3.11 | For BitBake |
| Git | 2.20 | 2.34+ | For submodules |
| GCC | 5.0 | 11.2.0 | Host compiler |
| Make | 3.82 | 4.3 | Build system |
| chrpath | 0.13 | 0.16 | RPATH manipulation |
| Perl | 5.16 | 5.34 | Build scripts |

### System Disk Space Requirements

| Item | Size | Note |
|------|------|------|
| Source repository | 2-3 GB | All layers + .git |
| Download cache | 5-10 GB | Package sources |
| Shared state cache | 10-15 GB | Incremental builds |
| Build output | 20-30 GB | Temporary build files |
| **Total** | **50-70 GB** | **Minimum free space** |

## Build Configuration

### Local Configuration (build/conf/local.conf)

**Critical settings for reproducibility:**

```bash
# Machine selection
MACHINE = "raspberrypi5"

# Image type
IMAGE_FEATURES = "debug-tweaks"

# Init system (MUST have BOTH lines)
DISTRO_FEATURES:append = " usrmerge wifi networking systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"

# Parallel compilation (adjust for system)
BB_NUMBER_THREADS = "$(nproc)"
PARALLEL_MAKE = "-j $(nproc)"

# Package format
PACKAGE_CLASSES = "package_ipk"

# Image type
IMAGE_FSTYPES = "wic.gz"

# Rootfs type
EXTRA_IMAGE_FEATURES = "allow-root-login"
```

### Layer Configuration (build/conf/bblayers.conf)

**Layer order matters!** Stack (from bottom to top):

```python
BBLAYERS ?= " \
    /path/to/layers/poky/meta \
    /path/to/layers/poky/meta-poky \
    /path/to/layers/meta-openembedded/meta-oe \
    /path/to/layers/meta-openembedded/meta-multimedia \
    /path/to/layers/meta-raspberrypi \
    /path/to/layers/meta-football \
"
```

**Why this order matters**:
1. **poky/meta** - Base recipes, lowest priority
2. **poky/meta-poky** - Poky-specific recipes
3. **meta-openembedded/meta-oe** - Community general recipes
4. **meta-openembedded/meta-multimedia** - Multimedia (camera, audio)
5. **meta-raspberrypi** - RPi-specific (device tree, kernel)
6. **meta-football** - Our customizations (highest priority)

This ensures our custom recipes override upstream defaults.

## Verification Checklist

After build, verify reproducibility:

### ✓ Image Properties
```bash
# Expected image name format
rpi5-minimal-raspberrypi5.rootfs-20240321120000.wic.gz

# Expected compressed size
~350-400 MB

# Expected uncompressed rootfs
~1.8-2.0 GB
```

### ✓ First Boot Verification
```bash
# Boot and SSH into device
ssh root@raspberrypi5.local

# Check kernel version
uname -a
# Should show: Linux raspberrypi5 ... armv8l ... GNU/Linux

# Check systemd (init system)
systemctl --version | head -1
# Should show: systemd XXX

# Check WiFi interface
ip link | grep wlan0

# Check camera
v4l2-ctl --list-devices
# Should show: /dev/video* entries for IMX477

# Boot time
systemd-analyze time
# Should be ~7-10 seconds (first boot ~15s with WiFi init)
```

## When Versions May Change

**Do NOT update layers unless:**
1. Security patches are needed
2. Bug fixes critical for build
3. New hardware support required

**If you do update a layer:**
1. Document the reason
2. Test the full build
3. Verify on hardware
4. Update this VERSIONS.md
5. Commit changes to main repo

## How to Reproduce Exact Build

```bash
# 1. Clone with exact versions
git clone --recursive https://github.com/wassimos69/pfe.git
cd pfe

# 2. Verify you're on correct commits (should be automatic with submodules)
git submodule status

# 3. Verify configuration files are unchanged
git status build/conf/

# 4. Build
export PATH=$PWD/layers/poky/bitbake/bin:$PATH
cd build
bitbake rpi5-minimal

# 5. Flash and boot
# (follow BUILD_INSTRUCTIONS.md)
```

## Troubleshooting Version Mismatches

### "Layer recipe conflicts"
**Cause**: Layer version mismatch or wrong order in bblayers.conf
**Fix**: 
```bash
git submodule update --init --recursive
cat build/conf/bblayers.conf | grep BBLAYERS
```

### "BitBake recipe not found"
**Cause**: Submodule not initialized or layer missing
**Fix**:
```bash
git submodule foreach git pull origin scarthgap
git status # should show all layers
```

### "Wrong image size"
**Cause**: Different layer versions producing different rootfs
**Fix**:
```bash
cd build
bitbake -c cleansstate rpi5-minimal
bitbake rpi5-minimal
```

---

**Last Updated**: April 2026  
**Build Test Date**: Tested on Ubuntu 22.04 LTS  
**Expected Build Time**: 2-3 hours (first build), 15-30 minutes (incremental)
