# Diagnostic - Caméra RPi5 Non Détectée

## 📋 Checklist de diagnostic à exécuter sur le Pi

Connectez-vous via `sudo picocom -b 115200 /dev/ttyUSB0` et exécutez ces commandes:

---

### 1️⃣ Vérifier les modules kernel chargés

```bash
root@raspberrypi5:~# lsmod | grep -E "imx477|unicam|cfe|pisp|v4l2"
```

**Résultat attendu:** Les modules doivent être listés
```
imx477                 24576  0
bcm2835_unicam         20480  0
rp1_cfe                36864  0
pisp_be                65536  1
videobuf2_v4l2         28672  1 pisp_be
```

**Si vides:** Les modules ne sont pas chargés au boot

---

### 2️⃣ Charger les modules manuellement

```bash
root@raspberrypi5:~# modprobe imx477
root@raspberrypi5:~# modprobe bcm2835_unicam
root@raspberrypi5:~# modprobe rp1_cfe
root@raspberrypi5:~# lsmod | grep imx477
```

---

### 3️⃣ Vérifier après chargement

```bash
root@raspberrypi5:~# ls -la /dev/video*
```

**Résultat attendu:**
```
crw-rw---- 1 root video 81,  0 Apr  1 12:00 /dev/video0
crw-rw---- 1 root video 81,  1 Apr  1 12:00 /dev/video1
```

---

### 4️⃣ Vérifier dmesg pour les erreurs CSI

```bash
root@raspberrypi5:~# dmesg | tail -50 | grep -iE "imx477|csi|camera|video|error"
```

**Chercher:** Erreurs avec CSI, caméra, ou imx477

---

### 5️⃣ Vérifier le device tree overlays

```bash
root@raspberrypi5:~# ls /boot/overlays/*.dtbo | grep -i camera
root@raspberrypi5:~# cat /proc/device-tree/base/axi/pcie@*/rp1/csi@*/status
```

**Résultat attendu:** Doit afficher `okay`

---

### 6️⃣ Vérifier config.txt

```bash
root@raspberrypi5:~# cat /boot/config.txt | grep -E "dtoverlay|camera"
```

**Doit contenir:**
```
dtoverlay=imx477
```

---

### 7️⃣ Tester libcamera après chargement

```bash
root@raspberrypi5:~# libcamera-hello --list-cameras
```

---

## 🔍 Analyse des Résultats

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| lsmod vide | Modules ne se chargent pas | Vérifier KERNEL_MODULE_AUTOLOAD dans image |
| /dev/video0 absent après modprobe | CSI pas activé | Vérifier config.txt et overlays |
| dmesg: "imx477 not found" | Caméra pas physiquement connectée | Vérifier câble CSI |
| dmesg: "CSI disabled" | Device tree overlay pas appliqué | Vérifier dtoverlay=imx477 |

---

## ⚠️ Causes courantes

1. **config.txt manque le dtoverlay**
   - Fichier: `/boot/config.txt`
   - Doit inclure: `dtoverlay=imx477`
   - Besoin de reboot après modification

2. **Modules non auto-chargés**
   - Le fichier image liste les modules mais ils peuvent ne pas se charger automatiquement
   - Vérifier `/etc/modules-load.d/` ou `/etc/modprobe.d/`

3. **CSI non activé dans le firmware**
   - Vérifier si le board supporte CSI
   - Checker les jumpers/connecteurs CSI1 vs CSI0

4. **Device tree overlay incorrect**
   - Vérifier que l'overlay est `imx477.dtbo` (pas autre variante)

---

## 📤 Rapportez-moi:

Exécutez ces commandes et partagez la sortie:

```bash
lsmod | grep imx477
ls -la /dev/video*
dmesg | tail -100
cat /boot/config.txt | grep -E "dtoverlay|camera"
```

Cela m'aidera à identifier précisément le problème!
