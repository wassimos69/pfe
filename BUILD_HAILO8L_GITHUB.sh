#!/bin/bash
# Build Hailo 8L depuis GitHub branche hailo8

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}"
cat << "BANNER"
╔══════════════════════════════════════════════════════════╗
║    🚀 BUILD HAILO 8L - GITHUB BRANCHE HAILO8           ║
╚══════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

BASE_DIR="/home/wassim/Bureau/yocto/pfe"
BUILD_DIR="$BASE_DIR/build"

# Vérifier prérequis
echo -e "${YELLOW}📋 Vérification des prérequis${NC}"
echo "=============================================="

if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}❌ Build dir not found: $BUILD_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build directory: $BUILD_DIR${NC}"

# Vérifier les recettes
if [ ! -f "$BASE_DIR/layers/meta-football/recipes-kernel/hailo-pci-8l/hailo-pci-8l_5.3.0.bb" ]; then
    echo -e "${RED}❌ hailo-pci-8l recipe not found${NC}"
    exit 1
fi

if [ ! -f "$BASE_DIR/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb" ]; then
    echo -e "${RED}❌ hailo-firmware-8l recipe not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Recettes Hailo 8L trouvées${NC}"

# Vérifier bblayers
if ! grep -q "meta-football" "$BUILD_DIR/conf/bblayers.conf"; then
    echo -e "${RED}❌ meta-football not in bblayers.conf${NC}"
    exit 1
fi

if ! grep -q "meta-hailo-libhailort" "$BUILD_DIR/conf/bblayers.conf"; then
    echo -e "${RED}❌ meta-hailo-libhailort not in bblayers.conf${NC}"
    exit 1
fi

echo -e "${GREEN}✅ bblayers.conf correctement configuré${NC}"

# Vérifier image
if ! grep -q "hailo-pci-8l" "$BASE_DIR/layers/meta-football/recipes-core/images/rpi5-minimal.bb"; then
    echo -e "${RED}❌ hailo-pci-8l not in image${NC}"
    exit 1
fi

if ! grep -q "hailo-firmware-8l" "$BASE_DIR/layers/meta-football/recipes-core/images/rpi5-minimal.bb"; then
    echo -e "${RED}❌ hailo-firmware-8l not in image${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Image rpi5-minimal correctement configurée${NC}"

# Résumé
echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 CONFIGURATION HAILO 8L${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""
echo -e "Build directory: ${GREEN}$BUILD_DIR${NC}"
echo -e "Driver: ${GREEN}hailo-pci-8l${NC} (GitHub hailo8 branch)"
echo -e "Firmware: ${GREEN}hailo-firmware-8l${NC} (GitHub hailo8 branch)"
echo -e "API: ${GREEN}libhailort${NC} (meta-hailo-libhailort)"
echo -e "Tools: ${GREEN}hailortcli, pyhailort, libgsthailo${NC}"
echo ""

# Demander confirmation
echo -e "${YELLOW}Démarrer le build maintenant? (y/n)${NC}"
read -p "" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Build annulé${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}⏳ COMPILATION EN COURS...${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""
echo "⏱️  Temps estimé: 45-90 minutes"
echo ""

cd "$BUILD_DIR"

bitbake rpi5-minimal

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ BUILD RÉUSSI!${NC}"
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo ""
    
    IMAGE=$(ls -lh "$BUILD_DIR/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs.wic.gz" 2>/dev/null | tail -1)
    if [ -n "$IMAGE" ]; then
        echo -e "${GREEN}Image générée:${NC}"
        echo "$IMAGE"
    fi
    
    echo ""
    echo "📝 Prochaines étapes:"
    echo "1. Flasher l'image sur carte SD: dd if=rpi5-minimal-...wic.gz of=/dev/sdX"
    echo "2. Démarrer Raspberry Pi 5"
    echo "3. Vérifier Hailo 8L:"
    echo "   $ modprobe hailo_pci"
    echo "   $ hailortcli fw-control"
else
    echo ""
    echo -e "${RED}❌ BUILD ÉCHOUÉ${NC}"
    exit 1
fi
