# 🔧 FIX FINAL - Overlays Device Tree

## Problème Identifié ✅

**Les overlays imx477.dtbo n'étaient pas inclus dans /boot/overlays/**

Cela explique pourquoi `dtoverlay=imx477` dans config.txt ne faisait rien - l'overlay n'existait pas!

---

## Solution Appliquée ✅

Créé: `layers/meta-football/recipes-bsp/bootfiles/rpi-bootfiles.bbappend`

Cette bbappend copy tous les overlays du firmware source vers `/boot/overlays/` lors du déploiement.

---

## Nouvelles Étapes

### Étape 1: Attendre la fin du build
```bash
# Vérifier les logs:
tail -f /tmp/build_log.txt
# Ou:
ps aux | grep bitbake
```

### Étape 2: Flash la nouvelle image

Une fois le build terminé:

```bash
# Sur votre ordinateur host
LATEST_IMAGE="/home/wassim/Bureau/yocto/clean/build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs-*.wic.gz"

sudo umount /dev/sda* 2>/dev/null || true
sudo gunzip -c $(ls $LATEST_IMAGE | tail -1) | \
  sudo dd of=/dev/sda bs=4M conv=fsync
sync
sudo eject /dev/sda
```

### Étape 3: Redémarrer le Pi

```bash
# Éjecter la carte SD du Pi
# Redémarrer le Pi avec la nouvelle image
```

### Étape 4: Vérifier que les overlays sont présents

Sur le Pi:
```bash
ls -la /boot/overlays/imx477.dtbo
# Faut afficher le fichier

ls /boot/overlays/ | wc -l
# Faut afficher un nombre > 0
```

### Étape 5: Redémarrer avec dtoverlay

Si les overlays ne sont pas là après flash:
```bash
# Vous avez peut-être besoin de reboot
reboot
```

### Étape 6: Vérifier la cam

```bash
libcamera-hello --list-cameras
```

---

## Résumé des Corrections

| Fichier | Changement | Raison |
|---------|-----------|--------|
| `rpi-bootfiles.bbappend` | Créé | Copier overlays du firmware vers /boot/overlays/ |
| `rpi-config_git.bbappend` | Déjà OK | dtoverlay=imx477 dans config.txt |
| `libcamera_0.4.0.bbappend` | Déjà OK | Pipeline RPi forcé |
| `rpi5-minimal.bb` | Modules OK | KERNEL_MODULE_AUTOLOAD correct |

---

## Si ça Fonctionne Pas

Après le nouvel flash, sur le Pi:

```bash
echo "=== Check 1: overlays existent ===" 
ls /boot/overlays/imx477.dtbo 2>&1

echo "=== Check 2: dtoverlay appliqué ===" 
grep dtoverlay /boot/config.txt

echo "=== Check 3: dmesg ===" 
dmesg | grep -iE "imx477|probe"

echo "=== Check 4: test caméra ===" 
libcamera-hello --list-cameras
```

Reportez TOUS les résultats! 🎯

---

## ETA

Build: ~20-30 minutes  
Flash: ~2 minutes  
Test: immediate après reboot
