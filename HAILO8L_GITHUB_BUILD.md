# 🚀 BUILD HAILO 8L - DEPUIS GITHUB

## ✅ CHANGEMENTS EFFECTUÉS

### 1. Driver PCIe Hailo 8L (NOUVEAU)
- **Fichier:** `pfe/layers/meta-football/recipes-kernel/hailo-pci-8l/hailo-pci-8l_5.3.0.bb`
- **Source:** GitHub `hailort-drivers` branche `hailo8`
- **URL:** `git://git@github.com/hailo-ai/hailort-drivers.git;branch=hailo8`
- **Output:** `hailo_pci.ko` (kernel module)

### 2. Firmware Hailo 8L (NOUVEAU)
- **Fichier:** `pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb`
- **Source:** GitHub `hailort-drivers` branche `hailo8`
- **Installation:** `/lib/firmware/hailo/hailo8l/`
- **Type:** Compilé depuis sources (pas téléchargé)

### 3. Image mise à jour
- **Fichier:** `pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb`
- **Packages inclus:**
  - ✅ `libhailort` (API compatible)
  - ✅ `hailortcli` (CLI Hailo)
  - ✅ `pyhailort` (Python bindings)
  - ✅ `hailo-pci-8l` (Driver PCIe 8L)
  - ✅ `hailo-firmware-8l` (Firmware 8L)
  - ✅ `libgsthailo` (GStreamer plugin)

### 4. Configuration Bitbake
- **bblayers.conf:** Gardé `meta-hailo-libhailort` pour libhailort existant
- **bblayers.conf:** Gardé `meta-football` pour nos recettes 8L

---

## 🎯 STRATÉGIE GITHUB

Au lieu de télécharger un firmware précompilé (qui n'existe pas pour 8L), on:
1. Clone le repo GitHub `hailort-drivers` branche `hailo8`
2. Compile le driver PCIe pour Hailo 8L
3. Extrait/compile le firmware depuis les sources
4. Utilise libhailort existant (API abstraite, compatible)

---

## 📋 PRÉREQUIS

- Accès internet pour cloner GitHub
- Git configuré avec clés SSH ou accès HTTPS
- ~1-2 GB d'espace disque supplémentaire (sources + compilation)

---

## 🚀 BUILD COMMAND

```bash
cd /home/wassim/Bureau/yocto/pfe/build
bitbake rpi5-minimal
```

**Temps estimé:** 45-90 minutes (compilations GitHub en plus)

---

## 📊 RÉSULTAT ATTENDU

```
✅ Image: rpi5-minimal-raspberrypi5.rootfs.wic.gz (~140 MB)
✅ Firmware: Hailo 8L uniquement
✅ Driver: Hailo 8L depuis branche hailo8
✅ API: libhailort (compatible)
```

---

## 🔧 FICHIERS CRÉÉS

```
pfe/layers/meta-football/
├── recipes-kernel/
│   └── hailo-pci-8l/
│       └── hailo-pci-8l_5.3.0.bb       (NOUVEAU)
└── recipes-hailo/
    ├── hailo-firmware-8l/
    │   └── hailo-firmware-8l_5.3.0.bb  (MODIFIÉ - GitHub au lieu de AWS)
    ├── libhailort-8l/                  (OPTIONNEL)
    ├── hailortcli-8l/                  (OPTIONNEL)
    ├── pyhailort-8l/                   (OPTIONNEL)
    └── libgsthailo-8l/                 (OPTIONNEL)
```

**Note:** Les recettes `-8l` optionnelles sont commentées pour le moment. On peut les utiliser plus tard si nécessaire.

---

## ✅ VERIFICATION PRÉ-BUILD

```bash
# Vérifier que les recettes existent
ls -la pfe/layers/meta-football/recipes-kernel/hailo-pci-8l/
ls -la pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/

# Vérifier l'image
grep "hailo-pci-8l\|hailo-firmware-8l" pfe/layers/meta-football/recipes-core/images/rpi5-minimal.bb

# Vérifier bblayers
grep "meta-football\|meta-hailo" pfe/build/conf/bblayers.conf
```

---

## 🆘 TROUBLESHOOTING

### Erreur: "git@github.com permission denied"
- Utiliser HTTPS au lieu de SSH dans les recettes
- Modifier `git://git@github.com/` en `https://github.com/`

### Erreur: "Cannot find firmware files"
- Les chemins de firmware dans `hailo-firmware-8l.bb` peuvent être incorrects
- À adapter selon la structure du repo hailo8

### Build lent / Timeout
- La première compilation depuis GitHub prend du temps
- Ajouter à local.conf: `BB_NUMBER_THREADS ?= "4"` ou plus selon votre CPU

---

## 📝 NOTES

- **Branche `hailo8`** contient le support Hailo 8L avec corrections/optimisations
- **AUTOREV** permet de toujours utiliser le dernier commit (développement actif)
- **libhailort existant** suffit - API est abstraite et compatible
- **SSH ou HTTPS:** Adapter les URL Git selon votre configuration

---

**Status:** ✅ Prêt pour BUILD  
**Date:** 28 avril 2026  
**Hailo:** 8L (depuis GitHub branche hailo8)
