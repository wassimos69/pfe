# 🚀 DÉMARRAGE RAPIDE - HAILO 8L

## ✅ Configuration complète

Hailo 8L est maintenant configuré pour compiler depuis **GitHub branche `hailo8`**

### Packages inclus:
```
✅ hailo-pci-8l       (Driver PCIe depuis GitHub hailo8)
✅ hailo-firmware-8l  (Firmware depuis GitHub hailo8)  
✅ libhailort         (API Hailo - meta-hailo-libhailort)
✅ hailortcli         (CLI - meta-hailo-libhailort)
✅ pyhailort          (Python - meta-hailo-libhailort)
✅ libgsthailo        (GStreamer - meta-hailo-libhailort)
```

---

## 🎯 LANCER LE BUILD

### Option 1: Script automatique (RECOMMANDÉ)
```bash
bash /home/wassim/Bureau/yocto/pfe/BUILD_HAILO8L_GITHUB.sh
```

### Option 2: Manuel
```bash
cd /home/wassim/Bureau/yocto/pfe/build
bitbake rpi5-minimal
```

---

## 📊 DURÉE ESTIMÉE

- **Premier build:** 60-90 minutes (téléchargement GitHub + compilation)
- **Builds suivants:** 20-40 minutes (cache)

---

## 📁 RECETTES CRÉÉES

**Driver Hailo 8L:**
- `/pfe/layers/meta-football/recipes-kernel/hailo-pci-8l/hailo-pci-8l_5.3.0.bb`

**Firmware Hailo 8L:**
- `/pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb`

**Image:**
- `/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb` (mise à jour)

---

## 🆘 EN CAS D'ERREUR

### Erreur: "git permission denied"
**Solution:** Modifier l'URL Git de SSH à HTTPS dans les recettes
```bash
# Changer de:
git://git@github.com/hailo-ai/...

# En:
https://github.com/hailo-ai/...
```

### Erreur: "Cannot find firmware"
**Solution:** Vérifier les chemins dans `hailo-firmware-8l_5.3.0.bb`
- Le repo hailo8 peut avoir une structure différente
- Adapter les chemins `install` si nécessaire

### Erreur: "Build timeout"
**Solution:** Augmenter les threads de compilation
```bash
# Dans pfe/build/conf/local.conf, ajouter:
BB_NUMBER_THREADS = "8"
PARALLEL_MAKE = "-j 8"
```

---

## ✅ POST-BUILD

Une fois le build réussi:

```bash
# Vérifier l'image
ls -lh /home/wassim/Bureau/yocto/pfe/build/tmp/deploy/images/raspberrypi5/rpi5-minimal-*.wic.gz

# Flasher sur carte SD (Linux/Mac)
dd if=/home/wassim/Bureau/yocto/pfe/build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs.wic.gz \
   of=/dev/sdX bs=4M status=progress

# Démarrer RPi5 et vérifier Hailo 8L
# Sur le device:
$ modprobe hailo_pci
$ hailortcli fw-control
```

---

## 📝 NOTES

- **Branche `hailo8`:** Contient optimisations et support 8L
- **AUTOREV:** Utilise toujours le dernier commit (développement)
- **libhailort existant:** Compatible avec driver 8L
- **Première clone:** Peut être lente (téléchargement GitHub)

---

## 📞 SUPPORT

Si des problèmes surviennent lors du build:
1. Vérifier la connectivité GitHub
2. Vérifier les permissions SSH/Git
3. Consulter les logs: `tail -100 /pfe/build/tmp/log/rpi5-minimal/`

---

**Status:** ✅ PRÊT POUR BUILD  
**Configuration:** Hailo 8L depuis GitHub  
**Date:** 28 avril 2026
