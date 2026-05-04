# LOCAL LAYER MODIFICATIONS

This document lists all modifications made to upstream layers for this project.

## meta-football (Our Custom Layer)

**Status**: ✓ Fully committed in submodule  
**Location**: `layers/meta-football/`  
**Purpose**: WiFi auto-configuration, Camera support, System optimization

### Recipes Provided

#### 1. WiFi Auto-Connection
- **File**: `recipes-connectivity/wifi-busybox/`
- **Components**:
  - `wifi-busybox.bb` - Main recipe
  - `wifi-up.sh` - WiFi startup script
  - `wifi-up.service` - systemd service file
  - `wpa_supplicant.conf` - Default WiFi config
- **Features**:
  - Auto-connects to WiFi on boot
  - Requires SSID/password in `/etc/wpa_supplicant/wpa_supplicant.conf`
  - Depends on wpa-supplicant and iw

#### 2. WPA Supplicant Configuration
- **File**: `recipes-connectivity/wpa-supplicant/wpa-supplicant_%.bbappend`
- **Modifications**: Enables WiFi scanning and connection

#### 3. Camera Support
- **File**: `recipes-multimedia/libcamera/libcamera_%.bbappend`
- **File**: `recipes-multimedia/libcamera-apps/libcamera-apps_git.bbappend`
- **Purpose**: Enable IMX477 camera module with PiSP

#### 4. Kernel Configuration
- **Location**: `recipes-kernel/linux/linux-raspberrypi_%.bbappend`
- **Config Files**:
  - `files/rp1-i2c-enable.cfg` - I2C for camera sensor
  - `files/boot-optimization.cfg` - Boot performance
  - `files/arm64-page-size-4k.cfg` - ARM64 optimization

#### 5. Minimal Image Definition
- **File**: `recipes-core/images/rpi5-minimal.bb`
- **Includes**: Base system + WiFi + Camera support
- **Size**: ~1.8-2.0 GB rootfs

#### 6. System Services
- **Location**: `recipes-core/images/files/`
- **Services**:
  - `camera-module-init.init` - Camera initialization
  - `net-ssh-rescue.init` - SSH availability
  - `rpi-rootfs-autogrow.init` - Filesystem expansion
  - `wpa_supplicant.init` - Legacy init support

#### 7. Network Configuration
- **File**: `recipes-core/init-ifupdown/init-ifupdown_1.0.bbappend`
- **Purpose**: Ensure network interfaces come up on boot

### Custom Kernel Patches

**If any**, they would be in: `recipes-kernel/linux/files/`  
**Current Status**: No custom patches, using standard meta-raspberrypi kernel

## meta-raspberrypi (Upstream: yoctoproject/meta-raspberrypi)

### Local Modifications

#### 1. Default Providers Configuration
- **File**: `conf/machine/include/rpi-default-providers.inc`
- **Changes**: *(document specific modifications)*

#### 2. LibCamera-Apps Recipe
- **File**: `dynamic-layers/multimedia-layer/recipes-multimedia/libcamera-apps/libcamera-apps_git.bb`
- **Changes**: *(document specific modifications)*

**To View Changes**:
```bash
cd layers/meta-raspberrypi
git status
git diff
git log --oneline -5
```

## meta-openembedded (Upstream: openembedded/meta-openembedded)

**Status**: ✓ Used as-is, no modifications  
**Components Used**:
- `meta-oe` - Base recipes
- `meta-multimedia` - ffmpeg, libcamera libraries

**No local changes required** - this layer is used upstream

## poky (Upstream: yoctoproject/poky)

**Status**: ✓ Used as-is, no modifications  
**Release**: 5.0.16 (Scarthgap)

**No local changes** - provides base Yocto distribution

## How These Modifications Work Together

```
┌─────────────────────────────────────────┐
│  Desired: Minimal RPi5 with WiFi+Cam   │
└──────────────┬──────────────────────────┘
               │
      ┌────────▼────────┐
      │  meta-football  │  ◄─ Our custom recipes
      │ (WiFi, Camera)  │
      └────────▲────────┘
               │
      ┌────────┴─────────┐
      │ meta-raspberrypi │  ◄─ RPi5 BSP + kernel
      └────────▲────────┘
               │
   ┌──────────┴──────────┐
   │ meta-openembedded   │  ◄─ Community libraries
   │ (FFmpeg, libcamera) │
   └──────────▲──────────┘
              │
      ┌───────┴────────┐
      │  poky (base)   │  ◄─ Core Yocto
      └────────────────┘
```

Each layer adds or overrides recipes from layers below it.

## How to Apply These Modifications

### From Scratch
```bash
git clone --recursive https://github.com/wassimos69/pfe.git
cd pfe

# All modifications are already applied via submodules
cd build
bitbake rpi5-minimal
```

### To Local Edits
If you need to modify recipes:

```bash
# Edit a recipe in meta-football
vim layers/meta-football/recipes-connectivity/wifi-busybox/wifi-busybox.bb

# Rebuild (BitBake tracks changes)
cd build
bitbake wifi-busybox -f -c compile
bitbake rpi5-minimal
```

## Removing/Reverting Modifications

If a modification causes issues:

```bash
# Revert a specific layer to upstream
cd layers/meta-raspberrypi
git pull origin scarthgap

# Return to pinned submodule version
cd ../..
git submodule update layers/meta-raspberrypi

# Rebuild
cd build
bitbake -c cleansstate rpi5-minimal
bitbake rpi5-minimal
```

## Contributing Improvements

If you improve a recipe:

1. **Test thoroughly** on RPi5 hardware
2. **Document** what changed and why
3. **Consider upstreaming** to yoctoproject if useful for community
4. **Update this document** with your changes

---

**For detailed recipe contents, see**:
- `layers/meta-football/` - Full recipe files
- `BUILD_INSTRUCTIONS.md` - How modifications are used
- `VERSIONS.md` - Version pinning for reproducibility
