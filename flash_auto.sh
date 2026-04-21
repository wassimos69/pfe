#!/bin/bash
# Script de flash automatisé avec overlay support

set -e

echo "========================================="
echo "FLASH AUTOMATISÉ - Caméra RPi5"
echo "========================================="
echo ""

# Chercher la plus nouvelle image
LATEST_IMAGE=$(ls -t /home/wassim/Bureau/yocto/clean/build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs-*.wic.gz 2>/dev/null | head -1)

if [ -z "$LATEST_IMAGE" ]; then
    echo "ERREUR: Aucune image trouvée!"
    exit 1
fi

echo "Image trouvée: $LATEST_IMAGE"
echo "Taille: $(ls -lh "$LATEST_IMAGE" | awk '{print $5}')"
echo ""

# Demander confirmation
lsblk
echo ""
read -p "Quel est le périphérique de la carte SD? (ex: sda): " DEVICE

if [ -z "$DEVICE" ]; then
    echo "ERREUR: Périphérique manquant"
    exit 1
fi

DEVICE="/dev/$DEVICE"

echo ""
echo "⚠️  ATTENTION: Vous allez écraser $DEVICE"
echo "Tout le contenu sera supprimé!"
read -p "Continuer? (OUI/non): " CONFIRM

if [ "$CONFIRM" != "OUI" ]; then
    echo "Annulé"
    exit 1
fi

echo ""
echo "Démontage..."
sudo umount ${DEVICE}* 2>/dev/null || true

echo "Éjection..."
sudo eject $DEVICE 2>/dev/null || true

echo "Flash en cours... (cela prend 2-3 minutes)"
sudo gunzip -c "$LATEST_IMAGE" | sudo dd of=$DEVICE bs=4M conv=fsync status=progress

echo ""
echo "Synchronisation..."
sync

echo "Éjection finale..."
sudo eject $DEVICE

echo ""
echo "✅ FLASH TERMINÉ!"
echo ""
echo "Prochaines étapes:"
echo "1. Insérez la carte dans le RPi"
echo "2. Démarrez le RPi"
echo "3. Attendez ~30 secondes"
echo "4. Connectez-vous via picocom: sudo picocom -b 115200 /dev/ttyUSB0"
echo "5. Testez: libcamera-hello --list-cameras"
echo ""
