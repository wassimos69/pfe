# 🔧 FIX IMMÉDIAT - CONFIG.TXT MANQUANT

## Problème Trouvé ✅

`dtoverlay=imx477` **MANQUE** de `/boot/config.txt`!

C'est pour ça que libcamera ne voit rien.

---

## SOLUTION RAPIDE (sur le Pi)

**Option 1: Ajouter manuellement (aujourd'hui)**

```bash
# Se placer root (vous l'êtes déjà)
cd /boot

# Faire une sauvegarde
cp config.txt config.txt.bak

# Ajouter la ligne (chercher la section [pi5])
nano config.txt

# Ajouter après [pi5]:
# camera_auto_detect=0
# dtoverlay=imx477
# gpu_mem=128

# Puis reboot
reboot
```

Voici le contenu pour ajouter dans config.txt:

```ini
[pi5]
camera_auto_detect=0
dtoverlay=imx477
gpu_mem=128
dtparam=cooling_fan=on
```

**Option 2: Via sed (ligne de commande)**

```bash
# Ajouter juste avant [all] ou à la fin:
echo "dtoverlay=imx477" >> /boot/config.txt
reboot
```

---

## SOLUTION COMPLÈTE (recompiler l'image)

Revenir sur la machine **HOST** (quitter picocom: CTRL-A puis CTRL-X)

Puis exécutez:

```bash
cd /home/wassim/Bureau/yocto/clean
source ./layers/poky/oe-init-build-env build >/dev/null 2>&1

# Nettoyer et recompiler rpi-config
bitbake -c cleansstate rpi-config
bitbake rpi5-minimal 2>&1 | tail -30
```

Puis flasher l'image sur la SD avec:
```bash
zcat build/tmp/deploy/images/raspberrypi5/rpi5-minimal-*.wic.gz | \
sudo dd of=/dev/sda bs=4M conv=fsync
```

---

## PRIORTY: Je recommande l'Option 2 (sed)

1. **Sur le Pi, exécutez immédiatement:**
```bash
echo "dtoverlay=imx477" >> /boot/config.txt
cat /boot/config.txt | tail -5  # Vérifier
reboot
```

2. **Attendez le reboot (~30 secondes)**

3. **Se reconnecter et tester:**
```bash
sudo picocom -b 115200 /dev/ttyUSB0
root / root
libcamera-hello --list-cameras
```

La caméra **DEVRAIT** être détectée maintenant! 🎥

---

## Après le Reboot

Dites-moi:
1. ✅ Caméra détectée? 
2. ❌ Toujours pas de caméra?

Je vais adapter la suite! 🚀
