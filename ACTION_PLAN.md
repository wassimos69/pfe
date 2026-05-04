# 🎯 Plan d'Action - Diagnostic Caméra Immédiat

Vous avez accès direct au Pi via UART. Voici **EXACTEMENT** ce qu'il faut faire:

---

## ÉTAPE 1️⃣ - Quitter picocom si nécessaire

Si picocom est ouvert, quittez avec: **`CTRL-A` puis `CTRL-X`**

---

## ÉTAPE 2️⃣ - Rouvrir picocom

```bash
sudo picocom -b 115200 /dev/ttyUSB0
# Login: root
# Password: root
```

---

## ÉTAPE 3️⃣ - Copier et exécuter la commande de diagnostic

Sur le Pi, copiez cette **commande simple** ligne par ligne:

```bash
echo "=== SETUP ===" && \
modprobe imx477 && echo "imx477: OK" || echo "imx477: FAIL" && \
modprobe bcm2835_unicam && echo "bcm2835_unicam: OK" || echo "bcm2835_unicam: FAIL" && \
modprobe rp1_cfe && echo "rp1_cfe: OK" || echo "rp1_cfe: FAIL" && \
echo "" && \
echo "=== MODULES CHARGÉS ===" && \
lsmod | grep -E "imx477|unicam|cfe|v4l2|video" || echo "AUCUN" && \
echo "" && \
echo "=== VIDÉO DEVICES ===" && \
ls -la /dev/video* 2>&1 || echo "AUCUN /dev/video*" && \
echo "" && \
echo "=== DMESG ERRORS ===" && \
dmesg | grep -iE "imx|csi|camera|error" | tail -20 || echo "AUCUNE ERREUR" && \
echo "" && \
echo "=== CONFIG ===" && \
grep -E "dtoverlay|camera" /boot/config.txt || echo "PAS DE CONFIG CAMÉRA" && \
echo "" && \
echo "=== LIBCAMERA TEST ===" && \
timeout 3 libcamera-hello --list-cameras 2>&1 || echo "TIMEOUT/ERREUR"
```

---

## ÉTAPE 4️⃣ - Rapportez-moi EXACTEMENT:

Copiez-collez **toute** la sortie et dites-moi:

1. **Les modules se chargent-ils?** (OK ou FAIL?)
2. **Des /dev/video* existent?**
3. **Des erreurs dans dmesg?**
4. **config.txt contient dtoverlay=imx477?**
5. **Résultat final de libcamera-hello?**

---

## 🚨 Cas Probables et Solutions

### Cas A: Tous les modules OK, /dev/video* exists, mais libcamera dit "no cameras"
→ **Problème libcamera pipeline**
→ Je dois recompiler libcamera avec le pipeline forcé

### Cas B: Modules FAIL à charger
→ **Problème KERNEL_MODULE_AUTOLOAD ou modules manquants**
→ Je dois vérifier les noms de modules

### Cas C: /dev/video* absent même après modprobe
→ **Problème CSI/Device Tree**
→ dmesg devrait montrer des erreurs

### Cas D: dmesg plein d'erreurs "CSI disabled" ou "camera not found"
→ **Problème matériel ou câble**
→ Vérifier connexion physique du câble CSI

---

## ⚡ Commande Ultra-Rapide

Si vous êtes pressé, copiez juste celle-ci:

```bash
modprobe imx477 && modprobe bcm2835_unicam && modprobe rp1_cfe && lsmod | grep -E "imx477|unicam|cfe" && ls /dev/video* && libcamera-hello --list-cameras
```

Puis **copiez tout ce qu'elle affiche** et reportez-moi!

---

## 📋 Qu'il faut absolument copier-coller ici après exécution:

```
<METTEZ LA SORTIE COMPLÈTE ICI>
```

J'attendrai vos résultats! 🔧
