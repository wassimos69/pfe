# 🔨 Corrections Potentielles - Basées sur le Diagnostic

Une fois le diagnostic exécuté, selon les résultats, voici les corrections à appliquer:

---

## Scénario 1️⃣: Modules OK → libcamera échoue

**Diagnostic:**
```
imx477: OK
bcm2835_unicam: OK
rp1_cfe: OK
/dev/video0 exists
libcamera-hello: ERROR *** no cameras available ***
```

**Cause:** Pipeline libcamera pas forcer correctement

**Correction dans Yocto:**

Éditer: `layers/meta-football/recipes-multimedia/libcamera/libcamera_0.4.0.bbappend`

```makefile
# Forcer le pipeline RPi
LIBCAMERA_PIPELINES:rpi = "rpi/vc4"

# Mais AUSSI ajouter ceci pour meson:
EXTRA_OEMESON:append:rpi = " \
    -Dpipelines=rpi/vc4 \
    -Dipas=rpi/vc4 \
    -Dcpp_args=-Wno-unaligned-access \
"

# ET s'assurer que PACKAGECONFIG est correct
PACKAGECONFIG:append:rpi = " rpi-v4l2"

# Logs de compilatiion
do_configure:append:rpi() {
    echo "=== Building libcamera with RPi pipeline rpi/vc4 ===" >&2
}
```

**Recompiler:**
```bash
cd /home/wassim/Bureau/yocto/clean
source ./layers/poky/oe-init-build-env build >/dev/null 2>&1
bitbake -c cleansstate libcamera
bitbake rpi5-minimal
```

---

## Scénario 2️⃣: Modules FAIL

**Diagnostic:**
```
imx477: FAIL
bcm2835_unicam: FAIL
rp1_cfe: FAIL
```

**Cause:** Noms de modules incorrects OU modules non compilés

**Correction:**

### A) Vérifier les noms:
```bash
# Sur le Pi, rechercher les modules:
find /lib/modules/$(uname -r) -name "*imx477*" -o -name "*unicam*"
```

### B) Si trouvés avec underscores/tirets différents:

Éditer: `layers/meta-football/recipes-core/images/rpi5-minimal.bb`

```makefile
# Trouver la ligne:
KERNEL_MODULE_AUTOLOAD += "imx477 bcm2835_unicam rp1_cfe videobuf2_v4l2"

# Remplacer par le bon nom trouvé dans find
KERNEL_MODULE_AUTOLOAD += "imx477 bcm2835_unicam rp1_cfe"

# OU si les noms utilisent des tirets:
KERNEL_MODULE_AUTOLOAD += "imx477 bcm2835-unicam rp1-cfe"
```

**Recompiler:**
```bash
bitbake -c cleansstate rpi5-minimal
bitbake rpi5-minimal
```

---

## Scénario 3️⃣: /dev/video* absent

**Diagnostic:**
```
Modules: OK
But: ls /dev/video* → AUCUN
```

**Cause:** Device Tree Overlay pas appliqué OU CSI désactivé

**Correction:**

### A) Vérifier config.txt:
```bash
# Sur le Pi:
grep "dtoverlay" /boot/config.txt
```

### B) Si absent, l'ajouter via bbappend:

Éditer: `layers/meta-football/recipes-bsp/bootfiles/rpi-config_git.bbappend`

Vérifier que cette ligne est présente:
```makefile
RPI_EXTRA_CONFIG += "dtoverlay=imx477\n"
```

**Ou remplacer entièrement le RPI_EXTRA_CONFIG:**

```makefile
RPI_EXTRA_CONFIG = "\
[pi5]\n\
camera_auto_detect=0\n\
dtoverlay=imx477,pwm1_2_pin=82\n\
gpu_mem=128\n\
[all]\n\
"
```

**Recompiler:**
```bash
bitbake -c cleansstate rpi-config
bitbake rpi5-minimal
```

---

## Scénario 4️⃣: dmesg affiche "CSI disabled"

**Diagnostic:**
```
dmesg output: "CSI is disabled" or similar
```

**Cause:** Firmware RaspberryPi pas configuré pour CSI

**Correction dans config.txt (via bbappend):**

```makefile
RPI_EXTRA_CONFIG = "\
[pi5]\n\
dtoverlay=imx477\n\
camera_auto_detect=0\n\
# S'assurer que CSI est activé (défaut):
# (habituellement pas besoin)
gpu_mem=128\n\
[all]\n\
"
```

Essayer aussi:
```makefile
RPI_EXTRA_CONFIG = "\
[pi5]\n\
dtdebug=1\n\
dtoverlay=imx477\n\
[all]\n\
"
```

---

## Scénario 5️⃣: Erreur "camera not detected" dans dmesg

**Diagnostic:**
```
dmesg: imx477: probe failed
Or: Camera not found on CSI bus
```

**Cause probables:**
1. Câble CSI mal connecté
2. Port CSI0 vs CSI1 incorrect  
3. Caméra défectueuse
4. Overlay imx477 pas le bon modèle

**Corrections:**
1. Vérifier **physiquement** le câble CSI
2. Essayer l'autre port CSI: `dtoverlay=imx477,csi_port=1`

Éditer bbappend:
```makefile
RPI_EXTRA_CONFIG = "\
[pi5]\n\
dtoverlay=imx477,csi_port=0\n\
[all]\n\
"
```

Ou:
```makefile
dtoverlay=imx477,csi_port=1
```

---

## 🆘 Si Rien Ne Marche

### Option 1: Forcer les modules à se charger au boot

Éditer: `layers/meta-football/recipes-core/images/rpi5-minimal.bb`

Ajouter un script postprocess qui crée `/etc/modules-load.d/camera.conf`:

```makefile
setup_camera_modules() {
    install -d ${IMAGE_ROOTFS}/etc/modules-load.d
    cat > ${IMAGE_ROOTFS}/etc/modules-load.d/camera.conf << 'EOF'
imx477
bcm2835_unicam
rp1_cfe
videobuf2_v4l2
EOF
}

ROOTFS_POSTPROCESS_COMMAND += "setup_camera_modules; "
```

### Option 2: Créer un service systemd qui charge les modules

```makefile
install_camera_service() {
    install -d ${IMAGE_ROOTFS}/etc/systemd/system
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/load-camera-modules.service << 'EOF'
[Unit]
Description=Load Camera Kernel Modules
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/sbin/modprobe imx477
ExecStart=/sbin/modprobe bcm2835_unicam
ExecStart=/sbin/modprobe rp1_cfe
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    # Enable it
    mkdir -p ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants
    ln -sf /etc/systemd/system/load-camera-modules.service \
           ${IMAGE_ROOTFS}/etc/systemd/system/multi-user.target.wants/load-camera-modules.service
}

ROOTFS_POSTPROCESS_COMMAND += "install_camera_service; "
```

---

## 📋 Checklist Recompilation

Après **CHAQUE** changement:

- [ ] Éditer le fichier .bbappend approprié
- [ ] `bitbake -c cleansstate <recipe>`
- [ ] `bitbake rpi5-minimal` (compile complet)
- [ ] `sudo gunzip -c build/tmp/deploy/.../rpi5-minimal-*.wic.gz | sudo dd of=/dev/sda bs=4M conv=fsync`
- [ ] Redémarrer le Pi
- [ ] Tester: `libcamera-hello --list-cameras`

---

## 🚀 Après le Diagnostic

**Me rapporter les résultats EXACTS** et je vous fournirai la correction précise!

Attendez vos résultats → Je vous dis quelle correction appliquer → Vous recompilez → Test! 🎯
