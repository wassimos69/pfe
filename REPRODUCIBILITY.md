# Build Reproducibility Guide

This document ensures you can reproduce the exact same Raspberry Pi 5 Yocto image without errors.

## ✅ Prerequisites Checklist

### 1. System Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Disk Space**: 100GB+ free (builds can use 50-80GB)
- **Arch**: x86_64 or aarch64

### 2. Essential Packages

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
  build-essential chrpath diffstat gawk git texinfo wget zlib1g-dev \
  liblz4-tool openssl python3-distutils \
  python3-dev python3-pip libssl-dev curl

# Fedora
sudo dnf install -y \
  git python3 python3-devel gcc g++ make perl wget \
  chrpath diffstat gawk texinfo zlib-devel

# Verify Python version (should be 3.8+)
python3 --version
```

## 🔄 Step-by-Step Build Process

### Step 1: Clone Repository with All Layers

```bash
# Clone with submodules (includes poky, meta-raspberrypi, meta-openembedded, meta-football)
git clone --recursive https://github.com/wassimos69/pfe.git
cd pfe

# Verify all layers are present
ls -la layers/
# Expected output:
# meta-football/          ← Our custom layer
# meta-openembedded/      ← Community recipes
# meta-raspberrypi/       ← Official Raspberry Pi BSP
# poky/                   ← Official Yocto distro
```

### Step 2: Check Out Correct Versions

```bash
cd pfe

# Verify main branch is checked out
git log -1 --oneline
# Should show: "Add all Yocto layers as submodules with local modifications"

# For each submodule, verify the commit
cd layers/poky && git log -1 --oneline && cd ../..
cd layers/meta-raspberrypi && git log -1 --oneline && cd ../..
cd layers/meta-openembedded && git log -1 --oneline && cd ../..
```

### Step 3: Initialize Build Environment

```bash
cd pfe

# Run setup script (installs Python dependencies)
bash setup.sh

# Or manually:
pip3 install -r requirements.txt

# Create build directory (if not present)
mkdir -p build

# Source Yocto environment
source poky/oe-init-build-env build
```

### Step 4: Verify Build Configuration

```bash
# The build/conf/local.conf should already be configured
# Check critical settings:

# ✅ Check machine is set correctly
grep "^MACHINE" build/conf/local.conf
# Should show: MACHINE = "raspberrypi5"

# ✅ Check init system is systemd
grep "^INIT_MANAGER" build/conf/local.conf
# Should show: INIT_MANAGER = "systemd"

# ✅ Check image recipe
grep "^IMAGE_INSTALL" build/conf/local.conf
# Should include: core-image-minimal, systemd, wpa-supplicant
```

### Step 5: Verify Layers Configuration

```bash
# Check bblayers.conf includes all necessary layers
cat build/conf/bblayers.conf

# Should reference:
# - meta-football     (custom layer with WiFi/Camera)
# - meta-raspberrypi  (RPi BSP)
# - meta-openembedded (OE community)
# - poky meta-* (core Yocto layers)
```

### Step 6: Start the Build

```bash
# From inside the build environment
cd pfe/build

# Build the image (this takes 30-90 minutes on first build)
bitbake rpi5-minimal

# Monitor progress
tail -f tmp/work/*/logs/log.do_compile

# Build is complete when you see:
# "Wrote 1 rootfs tarball to /path/to/deploy/images/raspberrypi5/"
```

### Step 7: Verify Image Output

```bash
cd pfe/build/tmp/deploy/images/raspberrypi5/

# List generated files
ls -lh

# Expected files:
# - core-image-minimal-raspberrypi5-xxxxxx.wic.gz     (5-7 GB compressed image)
# - core-image-minimal-raspberrypi5-xxxxxx.wic        (uncompressed)
# - rpi5-minimal-raspberrypi5-xxxxxx.rootfs.tar.bz2
# - *.testdata.json
```

## 🔍 Troubleshooting

### Issue: "No machine configuration found for 'raspberrypi5'"

**Solution**: Verify meta-raspberrypi layer is in bblayers.conf
```bash
grep "meta-raspberrypi" build/conf/bblayers.conf
# If missing, add it
```

### Issue: "Cannot find recipe for rpi5-minimal"

**Solution**: Verify meta-football layer is properly included
```bash
grep "meta-football" build/conf/bblayers.conf
# Check layers/meta-football/recipes-core/images/rpi5-minimal.bb exists
```

### Issue: "Python version too old"

**Solution**: Upgrade Python
```bash
python3 --version
# Should be 3.8 or higher
# For older systems: sudo apt install python3.10 python3.10-venv
```

### Issue: Disk space error during build

**Solution**: Clean build artifacts
```bash
cd pfe
bitbake -c clean rpi5-minimal
# Or clean everything (but keeps downloads)
bitbake -c cleansstate rpi5-minimal
```

## 📊 Build Configuration Matrix

The following configuration ensures reproducibility:

| Setting | Value | Location |
|---------|-------|----------|
| **Distribution** | poky | build/conf/local.conf |
| **Machine** | raspberrypi5 | build/conf/local.conf |
| **C Library** | musl | build/conf/local.conf |
| **Init System** | systemd | build/conf/local.conf |
| **Yocto Version** | Scarthgap (5.0.16) | layers/poky branch |
| **Meta-RPi Branch** | scarthgap | layers/meta-raspberrypi |
| **Meta-OE Branch** | scarthgap | layers/meta-openembedded |
| **Image Recipe** | rpi5-minimal | layers/meta-football/recipes-core/images/ |

## ✔️ Verification Checklist

After successful build, verify:

- [ ] All layers cloned with correct commits
- [ ] build/conf/local.conf has MACHINE="raspberrypi5"
- [ ] build/conf/local.conf has INIT_MANAGER="systemd"
- [ ] build/conf/bblayers.conf references all 4 layers
- [ ] No errors during `bitbake rpi5-minimal`
- [ ] .wic.gz image file created in deploy/images/raspberrypi5/
- [ ] Image size is 5-7 GB (compressed)

## 🚀 Deployment

Once the image is built:

```bash
# Flash to SD card
sudo bash flash_auto.sh

# Or manually:
cd pfe/build/tmp/deploy/images/raspberrypi5/
bzcat core-image-minimal-raspberrypi5-*.wic.gz | sudo dd of=/dev/sdX bs=4M status=progress
sync
```

## 📝 Notes

- **First build**: 30-90 minutes (compiles from source)
- **Incremental builds**: 5-20 minutes (reuses cached artifacts)
- **Build artifacts cache**: build/sstate-cache/ (can be large)
- **Downloaded sources**: build/downloads/ (reused across builds)

## 🔗 Reference Links

- [Yocto/BitBake Documentation](https://docs.yoctoproject.org/5.0/index.html)
- [Raspberry Pi Layer](https://github.com/agherzan/meta-raspberrypi)
- [Meta-OpenEmbedded](https://github.com/openembedded/meta-openembedded)
- [Our Custom Layer](./layers/meta-football)
