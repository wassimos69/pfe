# Complete Build Instructions for Raspberry Pi 5 Yocto Image

## 0. Clone the Repository with All Layers

```bash
# Clone with all submodules (Poky, meta-raspberrypi, meta-openembedded)
git clone --recursive https://github.com/wassimos69/pfe.git
cd pfe

# OR if you already cloned without --recursive
git clone https://github.com/wassimos69/pfe.git
cd pfe
git submodule update --init --recursive
```

**Expected structure after cloning:**
```
pfe/
├── layers/
│   ├── poky/                    (Yocto core)
│   ├── meta-raspberrypi/        (RPi Board Support Package)
│   ├── meta-openembedded/       (Community recipes)
│   └── meta-football/           (Our custom WiFi/Camera recipes)
├── build/conf/                  (BitBake configuration)
├── README.md
└── BUILD_INSTRUCTIONS.md
```

## 1. System Requirements

### Minimum Hardware
- **Disk Space**: 100GB free (recommended 150GB for multiple builds)
- **RAM**: 8GB minimum (16GB recommended)
- **CPU**: Multi-core processor (4+ cores)

### Operating System
- **Linux**: Ubuntu 20.04 LTS, 22.04 LTS, or Debian 11+
- **MacOS**: Tested on Intel/M1 (with GNU tools installed)
- **Windows**: WSL2 with Ubuntu 22.04

### Install Build Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    chrpath \
    curl \
    diffstat \
    gawk \
    git \
    libfile-copy-recursive-perl \
    liblocale-po-perl \
    libxml-sax-perl \
    python3 \
    python3-pip \
    python3-pexpect \
    python3-jinja2 \
    python3-distutils \
    openssh-client \
    wget \
    cpio \
    texinfo \
    lz4
```

#### Check Python version (should be 3.8+)
```bash
python3 --version
```

## 2. Setup Environment

### Option A: Automatic Setup (Recommended)
```bash
cd /path/to/pfe
source setup.sh
```

### Option B: Manual Setup
```bash
cd /path/to/pfe

# Add BitBake to PATH
export BUILDDIR=$PWD/build
export PATH=$PWD/layers/poky/bitbake/bin:$PATH

# Verify BitBake is accessible
bitbake --version
# Expected: BitBake Build Engine, Version X.X.X
```

## 3. Configuration Verification

Before building, verify the configuration files are correct:

```bash
# Check main configuration
cat build/conf/local.conf | grep -E "MACHINE|DISTRO|INIT"

# Expected output (key lines):
# MACHINE ??= "raspberrypi5"
# DISTRO_FEATURES:append = "usrmerge wifi networking systemd"
# VIRTUAL-RUNTIME_init_manager = "systemd"

# Check layer order
cat build/conf/bblayers.conf
```

**Expected bblayers order** (top to bottom):
1. `layers/poky/meta`
2. `layers/poky/meta-poky`
3. `layers/meta-openembedded/meta-oe`
4. `layers/meta-openembedded/meta-multimedia`
5. `layers/meta-raspberrypi`
6. `layers/meta-football` (custom layer)

## 4. Build the Yocto Image

### First Build (takes 2-3 hours)

```bash
cd build

# Start the build
bitbake rpi5-minimal

# Monitor build in another terminal (optional)
tail -f bitbake-cookerdaemon.log
```

### Expected Build Output
- Build should complete with **NO ERRORS**
- Final messages should show:
  ```
  NOTE: Tasks Summary: Attempted XXX tasks of which XXX didn't need to be rerun...
  NOTE: Build completed successfully.
  ```

### Incremental Builds (10-30 minutes)
If you modify recipes or configuration, subsequent builds are much faster:
```bash
cd build
bitbake rpi5-minimal
```

## 5. Locate the Generated Image

After successful build, the image file is at:
```
build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs-*.wic.gz
```

The `*` is a timestamp. Find the latest image:
```bash
ls -lh build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs-*.wic.gz | tail -1
```

**Image size**: ~350-400 MB (compressed), ~1.8 GB (uncompressed)

## 6. Flash to Raspberry Pi 5 SD Card

### Prerequisites
- SD Card (16GB minimum, UHS-II recommended for faster flashing)
- USB Card Reader
- Linux computer with `dd` command

### Flashing Process

#### Step 1: Identify SD Card Device
```bash
# List block devices BEFORE inserting SD card
lsblk

# Insert SD card in reader

# List again to find new device (likely /dev/sda, /dev/sdb, etc.)
lsblk

# Identify your SD card (watch for new device)
# ⚠️ BE ABSOLUTELY SURE - using wrong device will wipe data!
# Typical SD card: /dev/sda or /dev/sdb (NOT /dev/sda1 or /dev/sdb1)
```

#### Step 2: Unmount Partitions
```bash
# Unmount all partitions on the SD card (adjust device name)
sudo umount /dev/sda* 2>/dev/null || echo "Already unmounted"
```

#### Step 3: Flash Image
```bash
# Navigate to image directory
cd /path/to/pfe/build/tmp/deploy/images/raspberrypi5

# Flash image to SD card (⚠️ adjust /dev/sda if needed)
gunzip -c rpi5-minimal-raspberrypi5.rootfs-*.wic.gz | \
  sudo dd of=/dev/sda bs=4M status=progress conv=fsync

# Sync to ensure all data is written
sync

# Eject SD card
sudo eject /dev/sda
```

**Progress**: Should show ~450 MB written at ~20-50 MB/s

#### Step 4: Boot the Raspberry Pi 5
1. Remove SD card from reader
2. Insert into Raspberry Pi 5
3. Connect power (USB-C)
4. Wait ~10-15 seconds for first boot (WiFi initialization)

### First Boot

#### Serial Console Access (if UART header connected)
```bash
# Connect to UART at /dev/ttyUSB0
screen /dev/ttyUSB0 115200

# Or with picocom
picocom -b 115200 /dev/ttyUSB0
```

#### SSH Access (over WiFi)
```bash
# Default hostname and password from meta-football configuration
ssh root@raspberrypi5.local

# If hostname doesn't resolve, find IP
ping -c 1 raspberrypi5.local
# Then: ssh root@<IP>
```

## 7. Troubleshooting Build Errors

### Error: "Command 'bitbake' not found"
```bash
export PATH=$PATH:$(pwd)/layers/poky/bitbake/bin
bitbake --version
```

### Error: "Recipe conflicts in DISTRO_FEATURES"
**Problem**: systemd not properly enabled
**Solution**:
```bash
# In build/conf/local.conf, ensure BOTH lines are present:
DISTRO_FEATURES:append = " usrmerge wifi networking systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
```

### Error: "No recipe for camera support"
**Solution**: Verify meta-football layer is last in bblayers.conf
```bash
tail -5 build/conf/bblayers.conf
# Should show: layers/meta-football
```

### Build Timeout or OOM
```bash
# Reduce parallel builds in build/conf/local.conf
BB_NUMBER_THREADS = "4"    # Use 4 threads instead of CPU count
PARALLEL_MAKE = "-j 4"     # Use 4 parallel makes
```

### Clean and Rebuild
```bash
# Partial clean (keeps downloads)
cd build && bitbake rpi5-minimal -c cleansstate

# Full clean (delete everything except downloads)
cd build && bitbake rpi5-minimal -c clean
```

## 8. Verification Checklist

After first boot on Raspberry Pi 5:

```bash
# SSH into device
ssh root@raspberrypi5.local

# On device, verify components:

# ✓ Check systemd is init system
ps aux | grep "\[systemd\]"  # Should show systemd as PID 1

# ✓ Check WiFi connectivity
ip addr show wlan0            # Should have IP address

# ✓ Check camera is detected
v4l2-ctl --list-devices       # Should show /dev/video* entries

# ✓ Check boot time
systemd-analyze time          # Should show ~7 seconds total

# ✓ Check available storage
df -h                         # Should show root filesystem

# ✓ Check systemd services
systemctl list-units --type=service --state=running | grep -E "wifi|camera"
```

## 9. Version Information for Reproducibility

**Build Reproducibility**: This repository uses submodules to pin specific versions:

```bash
# Check current layer commits
cd pfe
git log --oneline -1 layers/poky
git log --oneline -1 layers/meta-raspberrypi
git log --oneline -1 layers/meta-openembedded
git log --oneline -1 layers/meta-football
```

**Key Versions**:
- **Yocto Release**: Scarthgap (Poky 5.0.16)
- **Machine**: Raspberry Pi 5 (ARMv8 64-bit)
- **Init System**: systemd 255.21+
- **C Library**: musl (lightweight, suitable for embedded)

## 10. Rebuilding After Repository Update

If the repository receives updates:

```bash
cd pfe
git pull origin main
git submodule update --init --recursive

# Then rebuild
cd build
bitbake -c cleansstate rpi5-minimal
bitbake rpi5-minimal
```

---

**For issues or questions**: Refer to individual diagnostic guides:
- `CAMERA_TEST_GUIDE.md` - Camera module troubleshooting
- `CORRECTIONS_GUIDE.md` - Common fixes
- `README_DIAGNOSTIC.md` - Diagnostic procedures
