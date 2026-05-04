#!/bin/bash
# Script pour obtenir les checksums réels du firmware Hailo 8L
# À exécuter AVANT le build

set -e

echo "=== Obtention des checksums Hailo 8L ==="
echo ""

# Variables
FW_URL="https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo8L/5.3.0/FW/hailo8l_fw.tar.gz"
LICENSE_URL="https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo8L/5.3.0/FW/LICENSE"
RECIPE_FILE="/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb"
TMP_DIR="/tmp/hailo8l_check"

# Créer répertoire temporaire
mkdir -p "$TMP_DIR"
cd "$TMP_DIR"

echo "📥 Téléchargement du firmware Hailo 8L depuis AWS..."
if wget -q "$FW_URL" -O hailo8l_fw.tar.gz; then
    echo "✅ Firmware téléchargé"
    FW_MD5=$(md5sum hailo8l_fw.tar.gz | awk '{print $1}')
    echo "   MD5 (firmware): $FW_MD5"
else
    echo "❌ Erreur: impossible de télécharger le firmware"
    echo "   URL: $FW_URL"
    echo "   Vérifiez votre connexion internet et les droits d'accès"
    exit 1
fi

echo ""
echo "📥 Téléchargement de la LICENSE..."
if wget -q "$LICENSE_URL" -O LICENSE; then
    echo "✅ LICENSE téléchargée"
    LICENSE_MD5=$(md5sum LICENSE | awk '{print $1}')
    echo "   MD5 (LICENSE): $LICENSE_MD5"
else
    echo "❌ Erreur: impossible de télécharger la LICENSE"
    echo "   URL: $LICENSE_URL"
    exit 1
fi

echo ""
echo "=== Mise à jour de la recette ==="
echo ""
echo "Remplacer dans $RECIPE_FILE:"
echo ""
echo "ANCIEN:"
echo "  md5sum=a6eb960bb021ce965a43c2cf2aa7041a \\"
echo "  ${BASE_URI}/${FW_AWS_DIR}/\${LICENSE_FILE};md5sum=263ee034adc02556d59ab1ebdaea2cda"
echo ""
echo "NOUVEAU:"
echo "  md5sum=$FW_MD5 \\"
echo "  ${BASE_URI}/${FW_AWS_DIR}/\${LICENSE_FILE};md5sum=$LICENSE_MD5"
echo ""

# Option automatique
read -p "Appliquer les changements automatiquement? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i "s/md5sum=a6eb960bb021ce965a43c2cf2aa7041a/md5sum=$FW_MD5/" "$RECIPE_FILE"
    sed -i "s/md5sum=263ee034adc02556d59ab1ebdaea2cda/md5sum=$LICENSE_MD5/" "$RECIPE_FILE"
    echo "✅ Recette mise à jour avec les checksums corrects"
else
    echo "⚠️  Mise à jour manuelle requise"
fi

echo ""
echo "=== Nettoyage ==="
rm -rf "$TMP_DIR"
echo "✅ Dossier temporaire nettoyé"

echo ""
echo "=== Prêt pour le build ==="
echo "Exécutez maintenant:"
echo "  cd /home/wassim/Bureau/yocto/pfe/build"
echo "  bitbake rpi5-minimal"
