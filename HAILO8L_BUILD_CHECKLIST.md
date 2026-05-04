# Checklist: Préparation Build Hailo 8L

## ✅ Configuration effectuée

### 1. Image et Packages Hailo
- [x] `rpi5-minimal.bb` mis à jour
- [x] Packages Hailo 8L inclus:
  - ✅ `hailo-firmware-8l` (firmware 8L à la place de 10H)
  - ✅ `hailo-pci` (driver PCI pour Hailo8)
  - ✅ `libhailort` (API Hailo)
  - ✅ `hailortcli` (CLI Hailo)
  - ✅ `pyhailort` (Python bindings)
  - ✅ `libgsthailo` (GStreamer plugin)

### 2. Recettes créées/modifiées
- [x] Nouvelle recette: `hailo-firmware-8l_5.3.0.bb`
  - Location: `pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/`
  - URL source: `Hailo8L/5.3.0/FW/hailo8l_fw.tar.gz`
  - Installation: `/lib/firmware/hailo/hailo8l/`

### 3. Configuration Bitbake
- [x] `bblayers.conf` nettoyé:
  - ❌ Supprimé: `meta-hailo-accelerator` (contient firmware 10H)
  - ✅ Gardé: `meta-hailo-libhailort` (libs et outils)
  - ✅ Gardé: `meta-football` (nos recettes custom)

### 4. Drivers Hailo supprimés
- [x] `hailo-firmware` (10H) → remplacé par `hailo-firmware-8l`
- [x] Autres drivers Hailo (10H, 15, VPU) → exclus

---

## ⚠️ À FAIRE AVANT LE BUILD

### 1. Obtenir les checksums corrects Hailo 8L
```bash
cd /home/wassim/Bureau/yocto/pfe
bash get-hailo8l-checksums.sh
```

Ce script va:
- Télécharger le firmware et la LICENSE depuis AWS S3
- Calculer les MD5 réels
- Mettre à jour automatiquement la recette avec les checksums

### 2. Vérifier la recette mis à jour
```bash
cat pfe/layers/meta-football/recipes-hailo/hailo-firmware-8l/hailo-firmware-8l_5.3.0.bb | grep md5sum
```

Les valeurs doivent être mises à jour (pas `a6eb960...` ni `263ee03...`)

### 3. Nettoyer ancien cache (optionnel mais recommandé)
```bash
cd /home/wassim/Bureau/yocto/pfe/build
bitbake-layers show-layers  # Vérifier que meta-hailo-accelerator n'est pas listé

# Nettoyer le cache
rm -rf bitbake.lock
rm -rf cache/
```

---

## 🚀 BUILD COMMAND

Une fois les checksums à jour:
```bash
cd /home/wassim/Bureau/yocto/pfe/build
source ../../openembedded-core/oe-init-build-env .
bitbake rpi5-minimal
```

Ou directement:
```bash
cd /home/wassim/Bureau/yocto/pfe/build
bitbake rpi5-minimal
```

---

## 📊 Résultat attendu

- Image finale: `rpi5-minimal-raspberrypi5.rootfs.wic.gz` (~130 MB compressé)
- Firmware inclus: **Hailo 8L uniquement**
- Autres drivers/firmware Hailo: **EXCLUS**

---

## 🔍 Post-build Verification

Après compilation, vérifier:
```bash
# Vérifier que le firmware 8L est présent
file_path="/home/wassim/Bureau/yocto/pfe/build/tmp/deploy/images/raspberrypi5/rpi5-minimal-raspberrypi5.rootfs.wic.gz"
if [ -f "$file_path" ]; then
    echo "✅ Image générée: $(ls -lh $file_path)"
else
    echo "❌ Erreur: image non trouvée"
fi
```

---

## 📝 Notes

- **Version Hailo**: 5.3.0
- **Architecture**: ARMv8 (Raspberry Pi 5)
- **Machine**: raspberrypi5
- **Distribution**: poky (Yocto Scarthgap)

---

## 🆘 Troubleshooting

### Erreur: "Cannot find hailo-firmware"
- → Vérifier que `hailo-firmware-8l` est dans `rpi5-minimal.bb`
- → Vérifier que `meta-football` est dans `bblayers.conf`

### Erreur: "md5sum mismatch"
- → Relancer: `bash get-hailo8l-checksums.sh`
- → Vérifier la connexion internet

### Erreur: "meta-hailo-accelerator not found"
- → Normal si on l'a supprimé de bblayers.conf (c'est intentionnel)
- → Vérifier les logs pour d'autres erreurs

---

Dernière mise à jour: 2026-04-28
