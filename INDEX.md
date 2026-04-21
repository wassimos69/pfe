# Raspberry Pi 5 Yocto Build Project - Documentation Index

## 🚀 Quick Start (5 minutes)

**First time cloning?** Start here:

```bash
git clone --recursive https://github.com/wassimos69/pfe.git
cd pfe
source setup.sh
cd build
bitbake rpi5-minimal
```

---

## 📚 Documentation Guide

### For New Users (Start Here)

1. **[README.md](README.md)** - Project overview and key specifications
   - What this project does
   - Key features (systemd, WiFi, Camera)
   - Repository structure

2. **[CHECKLIST_FIRST_BUILD.md](CHECKLIST_FIRST_BUILD.md)** - Pre-build verification
   - System requirements validation
   - Dependency installation
   - Configuration verification
   - ✓ Run this BEFORE first build

3. **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Complete build guide
   - Step-by-step clone instructions
   - Prerequisites and setup
   - Build commands
   - SD card flashing
   - First boot verification
   - Troubleshooting with solutions

### For Understanding the Project

4. **[VERSIONS.md](VERSIONS.md)** - Version information & reproducibility
   - Layer versions and commits
   - Build tool requirements
   - Why versions matter
   - How to reproduce exact builds

5. **[MODIFICATIONS.md](MODIFICATIONS.md)** - Local customizations
   - What was modified in each layer
   - Custom recipes (WiFi, Camera)
   - How modifications work together
   - Contributing improvements

### For Troubleshooting

6. **[CORRECTIONS_GUIDE.md](CORRECTIONS_GUIDE.md)** - Common issues & fixes
   - Build errors and solutions
   - Configuration problems
   - Reproducible error patterns

7. **[README_DIAGNOSTIC.md](README_DIAGNOSTIC.md)** - Diagnostic procedures
   - System information gathering
   - Build environment checking
   - Hardware verification

8. **[CAMERA_TEST_GUIDE.md](CAMERA_TEST_GUIDE.md)** - Camera module troubleshooting
   - Camera detection
   - Hardware testing
   - Known issues

### For Configuration Management

9. **[.env.example](.env.example)** - Environment configuration template
   - Build parameters
   - System settings
   - Copy and customize for your environment

10. **[requirements.txt](requirements.txt)** - Python dependencies
    - BitBake requirements
    - Install with: `pip3 install -r requirements.txt`

### Project-Specific Guides

11. **[CAMERA_DIAGNOSTIC.md](CAMERA_DIAGNOSTIC.md)** - Deep camera diagnostics
12. **[DEEP_DIAGNOSTIC.md](DEEP_DIAGNOSTIC.md)** - System-level diagnostics
13. **[DEPLOY_FIXED_IMAGE.md](DEPLOY_FIXED_IMAGE.md)** - Deployment procedures
14. **[FINAL_FIX.md](FINAL_FIX.md)** - Latest fixes and improvements
15. **[PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)** - Optimization details

---

## 🛠️ Utilities & Scripts

### Build Helpers

- **[setup.sh](setup.sh)** - Environment initialization script
  ```bash
  source setup.sh  # Sets up PATH, BitBake, environment
  ```

- **[flash_image.sh](flash_image.sh)** - Flash Yocto image to SD card
  ```bash
  ./flash_image.sh /dev/sda rpi5-minimal-*.wic.gz
  ```

- **[flash_auto.sh](flash_auto.sh)** - Automatic device detection flashing
  ```bash
  ./flash_auto.sh rpi5-minimal-*.wic.gz
  ```

- **[monitor-build.sh](monitor-build.sh)** - Monitor build progress
  ```bash
  ./monitor-build.sh
  ```

---

## 📊 Key File Structure

```
pfe/
├── build/conf/                          # BitBake configuration
│   ├── local.conf                       # Main build settings
│   └── bblayers.conf                    # Layer configuration
│
├── layers/
│   ├── poky/                            # Yocto core (submodule)
│   ├── meta-raspberrypi/                # RPi BSP (submodule)
│   ├── meta-openembedded/               # Community recipes (submodule)
│   └── meta-football/                   # Our custom layer
│       ├── recipes-connectivity/        # WiFi recipes
│       ├── recipes-multimedia/          # Camera recipes
│       └── recipes-kernel/              # Kernel customizations
│
├── Documentation/
│   ├── README.md                        # Main README
│   ├── BUILD_INSTRUCTIONS.md            # Full build guide
│   ├── CHECKLIST_FIRST_BUILD.md         # Pre-build checklist
│   ├── VERSIONS.md                      # Version info
│   ├── MODIFICATIONS.md                 # Local changes
│   └── ... (diagnostic guides)
│
├── Scripts/
│   ├── setup.sh                         # Environment setup
│   ├── flash_image.sh                   # Flash to SD card
│   ├── monitor-build.sh                 # Build monitoring
│   └── ... (utility scripts)
│
└── Configuration/
    ├── .env.example                     # Environment template
    ├── requirements.txt                 # Python dependencies
    ├── .gitignore                       # Git ignore rules
    └── .gitattributes                   # Line ending config
```

---

## 🔄 Workflow Guide

### First Build
```
1. Clone with --recursive
   └─> 2. Run CHECKLIST_FIRST_BUILD.md
       └─> 3. source setup.sh
           └─> 4. cd build && bitbake rpi5-minimal
               └─> 5. Follow BUILD_INSTRUCTIONS.md to flash
                   └─> 6. First boot on RPi5
```

### Troubleshooting Build Errors
```
1. Note error message
   └─> 2. Search CORRECTIONS_GUIDE.md
       └─> 3. Apply fix suggested
           └─> 4. Rebuild: bitbake rpi5-minimal
               └─> 5. If still failing, see DEEP_DIAGNOSTIC.md
```

### After Successful Build
```
1. Image at: build/tmp/deploy/images/raspberrypi5/
   └─> 2. Flash using flash_image.sh or flash_auto.sh
       └─> 3. Boot on RPi5
           └─> 4. Verify with VERIFICATION_GUIDE.md
               └─> 5. Deploy to production (DEPLOY_FIXED_IMAGE.md)
```

---

## 🎯 Common Tasks

### I want to...

**Build the image**
→ See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) Section 4

**Flash to SD card**
→ See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) Section 6

**Test the camera**
→ See [CAMERA_TEST_GUIDE.md](CAMERA_TEST_GUIDE.md)

**Troubleshoot errors**
→ See [CORRECTIONS_GUIDE.md](CORRECTIONS_GUIDE.md)

**Understand the configuration**
→ See [README.md](README.md) and [VERSIONS.md](VERSIONS.md)

**Modify recipes for WiFi/Camera**
→ See [MODIFICATIONS.md](MODIFICATIONS.md)

**Set up environment automatically**
→ Run `source setup.sh`

**Monitor the build**
→ Run `./monitor-build.sh`

**Diagnose system issues**
→ See [README_DIAGNOSTIC.md](README_DIAGNOSTIC.md)

---

## 📋 Recommended Reading Order

**For First Time (2-3 hours estimated)**
1. README.md (5 min) - Understand what this is
2. CHECKLIST_FIRST_BUILD.md (15 min) - Verify your system
3. BUILD_INSTRUCTIONS.md (30 min) - Understand build process
4. Start the build (2-3 hours)

**After First Build (30 min)**
5. VERSIONS.md (15 min) - Understand reproducibility
6. BUILD_INSTRUCTIONS.md Section 8 (15 min) - Verify first boot

**For Modifications (1-2 hours)**
7. MODIFICATIONS.md (20 min) - Understand custom recipes
8. README.md Section 2-3 (30 min) - Understand configuration
9. Explore meta-football/ layer files (optional)

---

## 🆘 Support & Issues

### If you encounter an error:

1. **Check CORRECTIONS_GUIDE.md first** - 80% of common issues documented
2. **Run diagnostics**: See README_DIAGNOSTIC.md
3. **Check layer versions**: See VERSIONS.md
4. **Verify configuration**: See CHECKLIST_FIRST_BUILD.md

### For camera issues:
- See CAMERA_TEST_GUIDE.md
- See CAMERA_DIAGNOSTIC.md
- See DEEP_DIAGNOSTIC.md (camera section)

### For build tool issues:
- Verify BitBake: `bitbake --version`
- Check layers: `bitbake-layers show-recipes`
- Re-run: `source setup.sh`

---

## 📞 Project Information

- **Target Device**: Raspberry Pi 5 (ARMv8 64-bit)
- **Yocto Release**: Scarthgap (Poky 5.0.16)
- **Init System**: systemd (with parallel boot)
- **Features**: WiFi, Camera (IMX477), SSH, Serial console
- **Boot Time**: ~7 seconds from kernel start to login
- **Repository**: https://github.com/wassimos69/pfe

---

## ✅ Checklist: Are You Ready?

Before starting a build, ensure:

- [ ] You've read README.md
- [ ] You've run CHECKLIST_FIRST_BUILD.md
- [ ] You have 50+ GB free disk space
- [ ] You have cloned with `--recursive`
- [ ] You have run `source setup.sh`
- [ ] You understand the project scope (embedded Linux)

**If all ✓**, you're ready to build! Start with [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).

---

**Last Updated**: April 21, 2026  
**Repository**: https://github.com/wassimos69/pfe  
**For the latest docs, clone or pull from main branch**
