# 🔧 Guide de Diagnostic Caméra - RPi5

## Problème Actuel
```
libcamera-hello: ERROR: *** no cameras available ***
```

Même après recompilation de l'image avec les modules kernel corrigés.

---

## 📥 Option 1: Diagnostic Via UART (Recommandé)

### Étape 1: Se connecter au Pi

```bash
# Sur votre ordinateur
sudo picocom -b 115200 /dev/ttyUSB0
# Login: root / Password: root
```

### Étape 2: Copier et exécuter le script de diagnostic

**Sur le Pi, créez le script:**
```bash
cat > /tmp/diagnostic.sh << 'EOF'
#!/bin/bash
OUTPUT="/tmp/diagnostic.txt"
{
    echo "=== DIAGNOSTIC CAMÉRA RPi5 ==="
    echo "Date: $(date)"
    echo ""
    
    echo "1. Modules kernel disponibles:"
    find /lib/modules/$(uname -r)/kernel/drivers -name "*.ko" 2>/dev/null | grep -E "imx477|unicam|cfe|v4l2" | sort
    
    echo ""
    echo "2. Charger les modules:"
    modprobe imx477 && echo "imx477: OK" || echo "imx477: FAIL"
    modprobe bcm2835_unicam && echo "bcm2835_unicam: OK" || echo "bcm2835_unicam: FAIL"
    modprobe rp1_cfe && echo "rp1_cfe: OK" || echo "rp1_cfe: FAIL"
    
    echo ""
    echo "3. Modules chargés:"
    lsmod | grep -E "imx477|unicam|cfe|v4l2|video"
    
    echo ""
    echo "4. Périphériques vidéo:"
    ls -la /dev/video* 2>/dev/null || echo "AUCUN /dev/video*"
    
    echo ""
    echo "5. Config.txt (filtré):"
    grep -E "dtoverlay|camera" /boot/config.txt || echo "PAS DE DTOVERLAY"
    
    echo ""
    echo "6. Erreurs dmesg (dernières 100 lignes):"
    dmesg | grep -iE "imx|camera|csi|video|error|fail" | tail -100
    
    echo ""
    echo "7. Test libcamera:"
    timeout 3 libcamera-hello --list-cameras 2>&1
    
} | tee "$OUTPUT"
echo "Sauvegardé dans: $OUTPUT"
EOF
chmod +x /tmp/diagnostic.sh
```

**Exécutez-le:**
```bash
/tmp/diagnostic.sh
```

**Affichez le résultat:**
```bash
cat /tmp/diagnostic.txt
```

Copiez **TOUT** le contenu et envoyez-le moi.

---

## 🔍 Hypothèses possibles

Basé sur le log "libcamera v0.4.0+dirty", voici ce qui pourrait être le problème:

### 1️⃣ Pipeline libcamera toujours "auto"
- La bbappend n'a peut-être pas forcé LIBCAMERA_PIPELINES
- Vérifier: `libcamera-hello --list-cameras -v 2>&1 | grep -i pipeline`

### 2️⃣ Modules kernel pas chargés
- Les noms avec underscores vs tirets peuvent ne pas matcher
- Vérifier: `modprobe --list | grep imx477`

### 3️⃣ Device Tree Overlay pas appliqué
- config.txt peut ne pas avoir `dtoverlay=imx477`
- Vérifier: `grep dtoverlay /boot/config.txt`

### 4️⃣ Caméra pas physiquement détectée
- Câble CSI déconnecté
- Mauvais port CSI
- Caméra défectueuse

### 5️⃣ Permissions utilisateur
- libcamera peut manquer de permissions
- Vérifier: `id`

---

## 🧪 Tests Progressifs

Une fois connecté au Pi, essayez ceci **dans l'ordre**:

```bash
# Test 1: Vérifier les modules
lsmod | grep imx477

# Test 2: Charger manuellement si absent
modprobe imx477
modprobe bcm2835_unicam
modprobe rp1_cfe

# Test 3: Vérifier après chargement
ls /dev/video*

# Test 4: Voir dmesg pour erreurs
dmesg | tail -50 | grep -iE "imx|csi|error"

# Test 5: Essayer libcamera
libcamera-hello --list-cameras -v

# Test 6: Essayer avec v4l2
v4l2-ctl --list-devices

# Test 7: Vérifier config.txt
cat /boot/config.txt | grep -E "dtoverlay|camera"

# Test 8: Vérifier overlays disponibles
ls /boot/overlays/ | grep -i imx
```

---

## 🚀 Si les modules se chargent MAIS libcamera échoue toujours

Cela indiquerait un problème dans **libcamera lui-même**, pas les modules.

**Actions:**
1. Vérifier que libcamera-apps est la bonne version: `pkg-config --modversion libcamera-apps`
2. Redémarrer: `reboot`
3. Vérifier le pipeline après reboot: `libcamera-hello --list-cameras -v`

---

## 🚀 Si les modules ne se chargent PAS

Cela signifie que KERNEL_MODULE_AUTOLOAD n'a pas fonctionné.

**Actions:**
1. Vérifier `/etc/modules-load.d/`: `ls -la /etc/modules-load.d/`
2. Vérifier `/etc/modprobe.d/`: `ls -la /etc/modprobe.d/`
3. Créer les fichiers manuellement si absent

---

## 📋 Informations à me rapporter:

Quand vous exécutez le diagnostic, dites-moi:

1. **Modules kernel chargés?** (lsmod output)
2. **/dev/video* existe?** (ls /dev/video* output)
3. **Erreurs dmesg?** (dmesg | grep -i error)
4. **config.txt correct?** (grep dtoverlay /boot/config.txt)
5. **libcamera version?** (`libcamera-hello --version`)
6. **Résultat exact de libcamera-hello après modprobe:**

```
modprobe imx477 && libcamera-hello --list-cameras
```

---

## 🔄 Plan d'action (après diagnostic)

1. Si modules chargés → Probable problème pipeline libcamera
2. Si modules absents → Probable problème KERNEL_MODULE_AUTOLOAD
3. Si /dev/video absent → Probable problème CSI/Device Tree
4. Si config.txt vide → Probable problème dtoverlay

Attendez ma réponse après le diagnostic! 🎯
