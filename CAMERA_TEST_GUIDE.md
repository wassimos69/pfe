# Guide de Test de Caméra - Raspberry Pi 5

## Configuration image rpi5-minimal
✅ **État**: Image correctement configurée pour la caméra
- **libcamera** (0.4.0) + **libcamera-apps** (1.4.2) inclus
- **v4l-utils** (1.26.1) disponible
- **Modules kernel** auto-chargés: imx477, bcm2835-unicam, rp1-cfe
- **PACKAGECONFIG**: rpi-v4l2 activé pour libcamera

---

## Procédure de Test sur le Raspberry Pi

### 1️⃣ Connexion au Pi via série
```bash
sudo picocom -b 115200 /dev/ttyUSB0
```

**Login:**
- Utilisateur: `root`
- Mot de passe: `root`

> 💡 **Raccourci quitter picocom**: Appuyer sur `CTRL-A` puis `CTRL-X`

---

### 2️⃣ Tests de détection de caméra

#### Test 1: Vérifier les périphériques vidéo
```bash
ls -la /dev/video*
```
**Résultat attendu**: Au moins `/dev/video0` doit être présent

#### Test 2: Lister les caméras avec libcamera
```bash
libcamera-hello --list-cameras
```
**Résultat attendu:**
```
Available cameras
0 : imx477 [4608x3456] (/base/axi/pcie@120000/rp1/csi@800000/csi-bridge@0)
```

#### Test 3: Dmesg pour diagnostiquer les erreurs
```bash
dmesg | grep -i camera
dmesg | grep -i imx477
dmesg | grep -i v4l2
```

---

### 3️⃣ Test de capture d'image

#### Capture avec libcamera-still
```bash
libcamera-still -o /tmp/test.jpg --timeout 1000
```

**Options utiles:**
- `--timeout 1000` : Attendre 1s avant de capturer
- `--encoding jpg` : Format JPEG (qualité compressée)
- `--width 1024 --height 768` : Résolution personnalisée

**Vérifier le fichier:**
```bash
ls -la /tmp/test.jpg
file /tmp/test.jpg
```

#### Test en temps réel (preview)
```bash
libcamera-hello --timeout 0
```
> Appuyer sur `CTRL-C` pour arrêter après quelques secondes

---

### 4️⃣ Tests v4l2-ctl (alternatives)

#### Lister les caméras
```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats
```

#### Capturer avec v4l2
```bash
v4l2-ctl -d /dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG
cat /dev/video0 > /tmp/test.raw
```

---

## 📋 Checklist de diagnostic

| Test | Commande | Résultat attendu |
|------|----------|------------------|
| Modules chargés | `lsmod \| grep imx477` | `imx477` visible |
| Périphérique vidéo | `ls /dev/video*` | `/dev/video0` existe |
| Détection libcamera | `libcamera-hello --list-cameras` | Affiche `imx477` |
| Capture image | `libcamera-still -o /tmp/test.jpg` | Fichier créé (~2-5 MB) |
| V4L2 info | `v4l2-ctl --list-devices` | Caméra listée |

---

## 🔴 Dépannage

### Erreur: `No cameras available`
```bash
# Vérifier les modules
lsmod | grep -E "imx477|bcm2835|pisp"

# Charger manuellement si nécessaire
modprobe imx477
modprobe bcm2835_unicam
```

### Erreur: `/dev/video0 not found`
```bash
# Vérifier les logs
dmesg | tail -50

# Vérifier si CSI est activé dans config.txt
cat /boot/config.txt | grep dtoverlay
```

### Erreur: `Permission denied`
```bash
# Ajouter l'utilisateur au groupe video
usermod -a -G video root
```

---

## 📸 Exemple de capture valide

```
root@raspberrypi5:~# libcamera-hello --list-cameras
Available cameras
0 : imx477 [4608x3456] (/base/axi/pcie@120000/rp1/csi@800000/csi-bridge@0)

root@raspberrypi5:~# libcamera-still -o /tmp/test.jpg --timeout 1000
[12:34:56.789] libcamera v0.4.0
[12:34:56.801] Starting camera...
[12:34:56.905] Camera started
[12:34:57.915] Captured image /tmp/test.jpg

root@raspberrypi5:~# ls -la /tmp/test.jpg
-rw-r--r-- 1 root root 3156789 Apr 01 12:34 /tmp/test.jpg
```

---

## 🔗 Ressources

- [libcamera documentation](https://libcamera.org/)
- [Raspberry Pi Camera Guide](https://www.raspberrypi.com/documentation/cameras-and-optics/)
- [Meta-raspberrypi layer](https://github.com/agherzan/meta-raspberrypi)
