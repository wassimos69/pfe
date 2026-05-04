#!/bin/bash
# DIAGNOSTIC COMPLET À COPIER-COLLER DANS PICOCOM
# Copiez la commande suivante et collez-la dans votre terminal picocom (CTRL-Shift-V)

# Commande complète en une seule ligne:

echo "=== DIAG ===" && lsmod | grep -E "imx477|unicam|cfe|v4l2|video" | head -10 && echo "---" && modprobe imx477 && modprobe bcm2835_unicam && modprobe rp1_cfe && echo "OK" && lsmod | grep -E "imx477|unicam|cfe" && ls -la /dev/video* 2>&1 | head -5 && dmesg | tail -50 | grep -iE "imx|csi|camera|error|fail" && grep -E "dtoverlay|camera" /boot/config.txt && echo "TEST:" && timeout 3 libcamera-hello --list-cameras 2>&1
