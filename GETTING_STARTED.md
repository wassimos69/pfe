# Repository Navigation Guide

Quick links to essential documentation for building and deploying the Raspberry Pi 5 Yocto image.

## 🚀 Quick Start (5 minutes)

1. **Clone the repository** with all layers:
   ```bash
   git clone --recursive https://github.com/wassimos69/pfe.git
   cd pfe
   ```

2. **Validate your system** is ready:
   ```bash
   bash validate-build.sh
   ```

3. **Follow the build instructions**:
   - Read: [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

## 📚 Documentation Index

### For First-Time Builders
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Complete step-by-step guide
- **[REPRODUCIBILITY.md](REPRODUCIBILITY.md)** - Ensure exact image reproduction
- **[CHECKLIST_FIRST_BUILD.md](CHECKLIST_FIRST_BUILD.md)** - Pre-build checklist
- **[setup.sh](setup.sh)** - Auto-setup script (Python dependencies)

### For Validation & Troubleshooting
- **[validate-build.sh](validate-build.sh)** - Run this before building to check all prerequisites
- **[VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md)** - Test the built image
- **[README_DIAGNOSTIC.md](README_DIAGNOSTIC.md)** - Debug boot issues

### Technical Documentation
- **[README.md](README.md)** - Project overview and specifications
- **[MODIFICATIONS.md](MODIFICATIONS.md)** - All custom modifications made
- **[VERSIONS.md](VERSIONS.md)** - Version matrix for reproducibility

### Camera & Connectivity
- **[CAMERA_TEST_GUIDE.md](CAMERA_TEST_GUIDE.md)** - Test libcamera on RPi5
- **[CAMERA_DIAGNOSTIC.md](CAMERA_DIAGNOSTIC.md)** - Troubleshoot camera issues
- **[DEBUG_CAMERA_UART.md](DEBUG_CAMERA_UART.md)** - Low-level camera debugging

### Deployment & Flashing
- **[flash_auto.sh](flash_auto.sh)** - Automated SD card flashing script
- **[flash_image.sh](flash_image.sh)** - Manual flashing with options
- **[DEPLOYMENT_SUMMARY.txt](DEPLOYMENT_SUMMARY.txt)** - Deployment checklist

### Optimization & Performance
- **[PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)** - Boot time analysis and optimization
- **[QUICK_FIX.md](QUICK_FIX.md)** - Common fixes and solutions

### Project Status
- **[RAPPORT_PFE_STRUCTURE.md](RAPPORT_PFE_STRUCTURE.md)** - Project report structure
- **[SYNTHESE_FAIT_NON_FAIT.md](SYNTHESE_FAIT_NON_FAIT.md)** - What's done/TODO

## 📁 Repository Structure

```
pfe/
│
├── 📄 Documentation Files
│   ├── README.md                        ← Start here for overview
│   ├── BUILD_INSTRUCTIONS.md            ← Step-by-step build guide
│   ├── REPRODUCIBILITY.md               ← Ensure exact reproduction
│   ├── MODIFICATIONS.md                 ← What was changed
│   └── ... (other guides)
│
├── 🔧 Build & Deployment Scripts
│   ├── setup.sh                         ← Install Python dependencies
│   ├── validate-build.sh                ← Check prerequisites
│   ├── monitor-build.sh                 ← Monitor build progress
│   ├── flash_auto.sh                    ← Auto-flash SD card
│   └── flash_image.sh                   ← Manual flash with options
│
├── build/                               ← BitBake build directory
│   ├── conf/
│   │   ├── local.conf                   ← Main Yocto config
│   │   ├── bblayers.conf                ← Layer configuration
│   │   └── templateconf.cfg
│   ├── downloads/                       ← Package source cache
│   ├── sstate-cache/                    ← Build artifact cache
│   └── tmp/
│       ├── work/                        ← Build work files
│       └── deploy/images/
│           └── raspberrypi5/            ← ✅ FINAL IMAGE HERE
│               └── core-image-minimal-raspberrypi5-*.wic.gz
│
├── layers/
│   ├── poky/                            ← Official Yocto distro
│   │   ├── meta-poky/
│   │   ├── meta-yocto-bsp/
│   │   └── ... (core layers)
│   │
│   ├── meta-raspberrypi/                ← Official RPi BSP
│   │   ├── conf/machine/raspberrypi5.conf
│   │   ├── recipes-bsp/
│   │   └── recipes-kernel/
│   │
│   ├── meta-openembedded/               ← Community recipes
│   │   ├── meta-oe/
│   │   ├── meta-networking/
│   │   ├── meta-python/
│   │   └── ...
│   │
│   └── meta-football/ ⭐ (OUR CUSTOM LAYER)
│       ├── conf/layer.conf              ← Layer definition
│       ├── recipes-bsp/                 ← Boot configuration
│       ├── recipes-connectivity/
│       │   ├── wifi-busybox/            ← WiFi auto-start
│       │   └── wpa-supplicant/          ← WiFi config
│       ├── recipes-core/
│       │   └── images/
│       │       └── rpi5-minimal.bb      ← Custom image recipe
│       └── recipes-multimedia/
│           ├── libcamera/               ← Camera support
│           └── libpisp/                 ← RPi ISP support
│
├── requirements.txt                     ← Python dependencies
├── VERSIONS.md                          ← Version matrix
└── ... (other documentation)
```

## ✅ Build Workflow

```
1. Clone Repository
   └─ git clone --recursive https://github.com/wassimos69/pfe.git

2. Validate System
   └─ bash validate-build.sh

3. Setup Environment
   └─ bash setup.sh
   └─ source poky/oe-init-build-env build

4. Configure Build
   └─ Edit build/conf/local.conf (already configured)
   └─ Edit build/conf/bblayers.conf (already configured)

5. Build Image
   └─ bitbake rpi5-minimal              (30-90 minutes)

6. Verify Output
   └─ ls build/tmp/deploy/images/raspberrypi5/
   └─ Image: core-image-minimal-raspberrypi5-*.wic.gz

7. Flash to SD Card
   └─ bash flash_auto.sh
   └─ OR: bzcat *.wic.gz | sudo dd of=/dev/sdX bs=4M

8. Boot & Verify
   └─ Test SSH, WiFi, Camera, Serial console
```

## 🔍 Key Files Reference

### Configuration Files (DO NOT MODIFY without understanding)
- `build/conf/local.conf` - Main Yocto configuration
  - `MACHINE = "raspberrypi5"`
  - `INIT_MANAGER = "systemd"`
  - `LIBC = "musl"`
  - Image recipe and other settings

- `build/conf/bblayers.conf` - Layer configuration
  - References to meta-football, meta-raspberrypi, meta-openembedded, poky

### Custom Layer (meta-football)
- `layers/meta-football/recipes-core/images/rpi5-minimal.bb` - Custom image recipe
- `layers/meta-football/recipes-connectivity/` - WiFi setup
- `layers/meta-football/recipes-multimedia/` - Camera support
- `layers/meta-football/recipes-bsp/` - Boot files

## 📊 Expected Build Specifications

| Parameter | Value |
|-----------|-------|
| **Target Device** | Raspberry Pi 5 (64-bit ARM) |
| **Yocto Release** | Scarthgap (5.0.16) |
| **Linux Kernel** | Latest RPi5 optimized |
| **Init System** | systemd |
| **C Library** | musl (smaller, faster) |
| **Image Size** | ~5-7 GB compressed |
| **Boot Time** | ~7.1 seconds to login |
| **Included Tools** | SSH, WiFi, Camera, Serial console |

## 🆘 Troubleshooting

### Build Issues
- **"No space left on device"** → `df -h` to check space; clean with `bitbake -c clean rpi5-minimal`
- **"Layer not found"** → Ensure all submodules are initialized with `git submodule update --init --recursive`
- **"Python version too old"** → `python3 --version` should be 3.8+

### Camera Issues
- Check: [CAMERA_DIAGNOSTIC.md](CAMERA_DIAGNOSTIC.md)
- Test: [CAMERA_TEST_GUIDE.md](CAMERA_TEST_GUIDE.md)

### Serial/UART Issues
- Check: [README_DIAGNOSTIC.md](README_DIAGNOSTIC.md)
- Wiring: TX→GPIO17, RX→GPIO27, GND→GND

## 📞 Support Links

- [Yocto Project Documentation](https://docs.yoctoproject.org/5.0/)
- [Raspberry Pi Forum](https://forums.raspberrypi.com/)
- [Meta-Raspberrypi GitHub](https://github.com/agherzan/meta-raspberrypi)
- [Bitbake Manual](https://docs.yoctoproject.org/bitbake/2.4/)

## ✨ Latest Updates

- ✅ All Yocto layers as Git submodules (easy updates)
- ✅ Reproducibility guide for exact builds
- ✅ Validation script to check prerequisites
- ✅ Custom WiFi and Camera recipes
- ✅ Optimized boot time (7.1s)
- ✅ Complete documentation

---

**Last Updated**: April 2026
**Repository**: https://github.com/wassimos69/pfe
