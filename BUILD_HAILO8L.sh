#!/bin/bash
# Script principal pour builder Hailo 8L

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}"
cat << "BANNER"
╔══════════════════════════════════════════════════════════╗
║        🚀 BUILD HAILO 8L - YOCTO RASPBERRY PI 5        ║
╚══════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

BASE_DIR="/home/wassim/Bureau/yocto/pfe"
BUILD_DIR="$BASE_DIR/build"

# ============================================
echo -e "${YELLOW}📋 ÉTAPE 1: Vérifier les prérequis${NC}"
echo "============================================"

if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}❌ Répertoire build non trouvé: $BUILD_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Répertoire build trouvé${NC}"

# ============================================
echo ""
echo -e "${YELLOW}📋 ÉTAPE 2: Obtenir les checksums Hailo 8L${NC}"
echo "============================================"

if ! grep -q "md5sum=a6eb960bb021ce965a43c2cf2aa7041a" "$BASE_DIR/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb" 2>/dev/null; then
    echo -e "${GREEN}✅ Checksums déjà mis à jour${NC}"
else
    echo -e "${YELLOW}⚠️  Checksums nécessitent mise à jour${NC}"
    read -p "Télécharger les checksums maintenant? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        bash "$BASE_DIR/get-hailo8l-checksums.sh"
    else
        echo -e "${RED}⚠️  Build ne peut pas continuer sans checksums valides${NC}"
        exit 1
    fi
fi

# ============================================
echo ""
echo -e "${YELLOW}📋 ÉTAPE 3: Vérifier la configuration${NC}"
echo "============================================"

if ! bash "$BASE_DIR/verify-hailo8l.sh"; then
    echo -e "${RED}❌ Vérification échouée${NC}"
    exit 1
fi

# ============================================
echo ""
echo -e "${YELLOW}📋 ÉTAPE 4: Préparer l'environnement build${NC}"
echo "============================================"

cd "$BUILD_DIR"

echo "Nettoyage du cache (optionnel)..."
if [ -f "bitbake.lock" ]; then
    rm -f bitbake.lock
    echo -e "${GREEN}✅ bitbake.lock supprimé${NC}"
fi

# ============================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        🎯 PRÊT POUR LE BUILD             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Répertoire: ${GREEN}$BUILD_DIR${NC}"
echo -e "Image: ${GREEN}rpi5-minimal${NC}"
echo -e "Hailo: ${GREEN}8L (5.3.0)${NC}"
echo ""

# ============================================
echo -e "${YELLOW}Démarrer le build maintenant? (y/n)${NC} "
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo -e "${BLUE}⏳ BUILD EN COURS...${NC}"
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo ""
    
    bitbake rpi5-minimal
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${BLUE}════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✅ BUILD RÉUSSI!${NC}"
        echo -e "${BLUE}════════════════════════════════════════════${NC}"
        echo ""
        echo "Image générée:"
        ls -lh "$BUILD_DIR/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs.wic.gz" 2>/dev/null || echo "Image non trouvée"
        echo ""
        echo "Prochaines étapes:"
        echo "1. Copier l'image sur une carte SD"
        echo "2. Démarrer le Raspberry Pi 5"
        echo "3. Vérifier que Hailo 8L est bien détecté"
        echo ""
        echo "Pour vérifier Hailo 8L sur le système:"
        echo "  $ modprobe hailo_pci"
        echo "  $ hailortcli fw-control"
    else
        echo -e "${RED}❌ BUILD ÉCHOUÉ${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Build annulé${NC}"
    echo "Pour relancer le build, exécutez:"
    echo "  cd $BUILD_DIR"
    echo "  bitbake rpi5-minimal"
fi
