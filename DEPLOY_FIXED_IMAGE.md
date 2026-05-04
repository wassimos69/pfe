# Guide de Déploiement - Image RPi5 Corrigée avec Caméra

## 🔧 Correction Appliquée

**Problème résolu**: "No cameras available" avec libcamera  
**Cause**: L'auto-détection du pipeline libcamera échouait sur Raspberry Pi 5

### Fichier de correctif créé

📄 [libcamera_0.4.0.bbappend](layers/meta-football/recipes-multimedia/libcamera/libcamera_0.4.0.bbappend)

```makefile
# Force le pipeline Raspberry Pi pour libcamera
LIBCAMERA_PIPELINES:rpi = "rpi/vc4"
PACKAGECONFIG:append:rpi = " rpi-v4l2"

EXTRA_OEMESON:append:rpi = " \
    -Dipas=rpi/vc4 \
    -Dcpp_args=-Wno-unaligned-access \
"
```

---

## 📦 Nouvelle Image

**Fichier compilé:**
```
build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs-20260401104059.wic.gz
```

**Taille:** ~145 MB (compressée)  
**Composants de caméra inclus:**
- ✅ libcamera 0.4.0 (pipeline RPi forcé)
- ✅ libcamera-apps 1.4.2  
- ✅ v4l-utils 1.26.1
- ✅ media-ctl
- ✅ Modules kernel: imx477, bcm2835-unicam, rp1-cfe

---

## 📥 Déploiement sur Raspberry Pi 5

### 1️⃣ Flasher l'image sur une carte SD

```bash
# Identifier la carte SD (attention: cela efface tout!)
lsblk

# Décompresser et flasher (remplacer sdX par votre carte)
zcat rpi5-minimal-raspberrypi5.rootfs-20260401104059.wic.gz | sudo dd of=/dev/sdX bs=4M status=progress
sudo sync

# Éjecter la carte
sudo eject /dev/sdX
```

### 2️⃣ Démarrer le Raspberry Pi 5

- Insérer la carte SD
- Connecter l'alimentation
- Attendre ~30 secondes pour le boot complet

### 3️⃣ Connexion série (host)

```bash
sudo picocom -b 115200 /dev/ttyUSB0
# Login: root / Password: root
```

---

## ✅ Tester la Caméra

### Test 1: Vérifier la détection
```bash
root@raspberrypi5:~# libcamera-hello --list-cameras
Available cameras
0 : imx477 [4608x3456] (/base/axi/pcie@120000/rp1/csi@800000/csi-bridge@0)
```

**Résultat attendu:** Doit afficher la caméra imx477

### Test 2: Capturer une image
```bash
root@raspberrypi5:~# libcamera-still -o /tmp/test.jpg --timeout 1000
[12:34:56.789] libcamera v0.4.0
[12:34:56.801] Starting camera...
[12:34:56.905] Camera started
[12:34:57.915] Captured image /tmp/test.jpg

root@raspberrypi5:~# ls -la /tmp/test.jpg
-rw-r--r-- 1 root root 3156789 Apr 01 12:34 /tmp/test.jpg
```

**Résultat attendu:** Fichier image créé (~2-5 MB)

### Test 3: Preview temps réel
```bash
root@raspberrypi5:~# libcamera-hello --timeout 0
```

**Résultat attendu:** L'affichage de la caméra s'active (appuyer CTRL-C pour arrêter)

---

## 🔧 Dépannage

### ❌ Erreur: "No cameras available"

**Confirmez que la correction a été appliquée:**
```bash
# Dans le host (après recompilation)
grep -r "LIBCAMERA_PIPELINES" \
  layers/meta-football/recipes-multimedia/libcamera/

# Doit afficher:
# LIBCAMERA_PIPELINES:rpi = "rpi/vc4"
```

**Vérifiez les modules kernel:**
```bash
root@raspberrypi5:~# lsmod | grep -E "imx477|unicam|cfe|pisp"
imx477                 24576  0
bcm2835_unicam         20480  0
rp1_cfe                36864  0
pisp_be                65536  1
```

### ❌ Erreur: CSI Board pas détectée

**Vérifier device tree:**
```bash
root@raspberrypi5:~# cat /proc/device-tree/base/axi/pcie@*/rp1/csi@*/status
okay
```

### ❌ Erreur: Permission denied

**Sur le Pi (si nécessaire):**
```bash
root@raspberrypi5:~# usermod -a -G video root
```

---

## 📊 Vérification d'intégrité

**Checksums de l'image:**
```bash
# Sur votre host pour vérifier l'intégrité
sha256sum rpi5-minimal-raspberrypi5.rootfs-20260401104059.wic.gz
```

**Backup de la configuration:**
```bash
# Sauvegarder l'image compilée
cp build/tmp/deploy/images/raspberrypi5/rpi5-minimal-*.wic.gz \
   ~/backups/rpi5-minimal-$(date +%Y%m%d).wic.gz
```

---

## 🔗 Fichiers clés

- [Image corrigée](build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs-20260401104059.wic.gz)
- [Correctif libcamera](layers/meta-football/recipes-multimedia/libcamera/libcamera_0.4.0.bbappend)
- [Configuration image](layers/meta-football/recipes-core/images/rpi5-minimal.bb)
- [Local conf](build/conf/local.conf)

---

## 📝 Notes

- Le correctif force le pipeline RPi pour **toutes les machines avec SOC_FAMILY=rpi**
- Cela inclut: raspberrypi5, raspberrypi-armv8, et autres variantes RPi
- Le plugin libcamera rpi/vc4 est maintenant intégré lors de la compilation
