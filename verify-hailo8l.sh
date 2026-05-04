#!/bin/bash
# Script de vérification de la configuration Hailo 8L

echo "🔍 === VÉRIFICATION CONFIGURATION HAILO 8L ===" 
echo ""

ERRORS=0
WARNINGS=0

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    local file=$1
    local name=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $name existe"
        return 0
    else
        echo -e "${RED}❌${NC} $name MANQUANT: $file"
        ((ERRORS++))
        return 1
    fi
}

check_contains() {
    local file=$1
    local pattern=$2
    local name=$3
    if grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✅${NC} $name trouvé"
        return 0
    else
        echo -e "${RED}❌${NC} $name INTROUVABLE dans $(basename $file)"
        ((ERRORS++))
        return 1
    fi
}

check_not_contains() {
    local file=$1
    local pattern=$2
    local name=$3
    if ! grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✅${NC} $name correctement supprimé"
        return 0
    else
        echo -e "${RED}❌${NC} $name TOUJOURS PRÉSENT dans $(basename $file)"
        ((ERRORS++))
        return 1
    fi
}

# ============================================
echo "📋 1. VÉRIFICATION DES RECETTES"
echo "============================================"

check_file "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb" \
    "Recette Hailo 8L"

if [ -f "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb" ]; then
    check_contains \
        "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb" \
        "Hailo8L" \
        "URL Hailo 8L correcte"
fi

# ============================================
echo ""
echo "📋 2. VÉRIFICATION IMAGE (rpi5-minimal.bb)"
echo "============================================"

check_file "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb" \
    "Image rpi5-minimal"

if [ -f "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb" ]; then
    check_contains \
        "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb" \
        "hailo-firmware-8l" \
        "Package hailo-firmware-8l inclus"
    
    check_not_contains \
        "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb" \
        "hailo-firmware \\\\" \
        "Ancienne recette hailo-firmware"
    
    check_contains \
        "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb" \
        "hailo-pci" \
        "Driver Hailo PCI inclus"
    
    check_contains \
        "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb" \
        "libhailort" \
        "LibHailoRT inclus"
fi

# ============================================
echo ""
echo "📋 3. VÉRIFICATION BBLAYERS.CONF"
echo "============================================"

check_file "/home/wassim/Bureau/yocto/pfe/build/conf/bblayers.conf" \
    "Configuration bblayers"

if [ -f "/home/wassim/Bureau/yocto/pfe/build/conf/bblayers.conf" ]; then
    check_contains \
        "/home/wassim/Bureau/yocto/pfe/build/conf/bblayers.conf" \
        "meta-hailo-libhailort" \
        "Couche meta-hailo-libhailort activée"
    
    check_contains \
        "/home/wassim/Bureau/yocto/pfe/build/conf/bblayers.conf" \
        "meta-football" \
        "Couche meta-football activée"
    
    check_not_contains \
        "/home/wassim/Bureau/yocto/pfe/build/conf/bblayers.conf" \
        "meta-hailo-accelerator" \
        "Couche meta-hailo-accelerator (contient firmware 10H)"
fi

# ============================================
echo ""
echo "📋 4. VÉRIFICATION DES CHECKSUMS"
echo "============================================"

if grep -q "md5sum=a6eb960bb021ce965a43c2cf2aa7041a" "/home/wassim/Bureau/yocto/pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb"; then
    echo -e "${YELLOW}⚠️ ${NC} Checksums encore en placeholder (valeurs par défaut)"
    echo "   À faire: bash /home/wassim/Bureau/yocto/pfe/get-hailo8l-checksums.sh"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅${NC} Checksums mis à jour"
fi

# ============================================
echo ""
echo "📋 5. VÉRIFICATION DES FICHIERS DE CONFIGURATION"
echo "============================================"

check_file "/home/wassim/Bureau/yocto/pfe/get-hailo8l-checksums.sh" \
    "Script checksums"

check_file "/home/wassim/Bureau/yocto/pfe/HAILO8L_BUILD_CHECKLIST.md" \
    "Documentation Hailo 8L"

# ============================================
echo ""
echo "📊 === RÉSUMÉ ===" 
echo "============================================"
echo -e "Erreurs: ${RED}$ERRORS${NC}"
echo -e "Avertissements: ${YELLOW}$WARNINGS${NC}"

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Configuration OK - PRÊT POUR LE BUILD${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "1️⃣  Obtenir checksums: bash /home/wassim/Bureau/yocto/pfe/get-hailo8l-checksums.sh"
    echo "2️⃣  Vérifier: bash /home/wassim/Bureau/yocto/pfe/verify-hailo8l.sh"
    echo "3️⃣  Builder: cd pfe/build && bitbake rpi5-minimal"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Configuration INCOMPLÈTE - Corriger les erreurs ci-dessus${NC}"
    exit 1
fi
