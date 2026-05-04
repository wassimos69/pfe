# 🔍 DIAGNOSTIC APPROFONDI - Caméra Toujours Non Détectée

Même après `dtoverlay=imx477` et reboot, la caméra n'existe toujours pas?

Il y a plusieurs causes possibles. Exécutez ceci sur le Pi:

---

## ÉTAPE 1: Vérifier que dtoverlay est chargé

```bash
# Voir les overlays chargés:
cat /proc/device-tree/base/axi/pcie@*/rp1/csi@*/status 2>/dev/null && echo "CSI OK" || echo "CSI NOT FOUND"

# Vérifier le device tree:
ls -la /proc/device-tree/base/
```

**Résultat attendu:** `okay` = CSI activé

---

## ÉTAPE 2: Vérifier que l'overlay imx477.dtbo existe

```bash
# Chercher l'overlay:
ls /boot/overlays/imx477*

# Chercher TOUS les overlays caméra:
ls /boot/overlays/ | grep -iE "camera|imx|csi"
```

**Si aucun imx477.dtbo:** C'est le problème!

---

## ÉTAPE 3: Vérifier dmesg après reboot

```bash
# Voir si des erreurs caméra:
dmesg | grep -iE "imx477|camera|csi|probe|failed|error" | head -50
```

**Chercher:**
- "imx477 probe failed"
- "CSI is disabled" 
- "Camera not found"

---

## ÉTAPE 4: Vérifier le câble CSI

```bash
# Vérifier device tree pour CSI:
cat /proc/device-tree/base/axi/pcie@*/rp1/csi@*/status

# Vérifier tous les nœuds CSI:
find /proc/device-tree -name "*csi*" -o -name "*camera*" 2>/dev/null
```

---

## ÉTAPE 5: Vérifier dmesg pour caméra détectée

```bash
# Voir TOUTES les erreurs + infos caméra:
dmesg | grep -iE "imx|media|camera" | tail -100
```

---

## ÉTAPE 6: Vérifier S'il y a des logs de probe

```bash
# Voir qui utilise les bus vidéo:
ls -la /sys/class/video4linux/

# Voir les périphériques I2C:
i2cdetect -l

# Vérifier sur le bus I2C2:
i2cdetect -y 2  # ou essayer 0, 1, 3...
```

La caméra devrait s'afficher à une adresse I2C (ex: 0x10 pour imx477)

---

## ÉTAPE 7: Essayer des overlays alternatifs

```bash
# Essayer avec parameters:
echo "dtoverlay=imx477,pwm1_2_pin=82" >> /boot/config.txt
reboot
```

Ou:
```bash
# Essayer autre port CSI:
echo "dtoverlay=imx477,csi_port=0" >> /boot/config.txt
reboot
```

Ou:
```bash
# Essayer sur CSI1:
echo "dtoverlay=imx477,csi_port=1" >> /boot/config.txt
reboot
```

---

## 🆘 DIAGNOSTIC COMPLET À FAIRE:

Exécutez ces commandes et **copiez TOUT:**

```bash
echo "=== 1. CSI STATUS ===" && \
cat /proc/device-tree/base/axi/pcie@*/rp1/csi@*/status 2>/dev/null && \
echo "" && \
echo "=== 2. OVERLAYS EXISTANTS ===" && \
ls /boot/overlays/ | grep -iE "camera|imx|csi" && \
echo "" && \
echo "=== 3. CONFIG.TXT ===" && \
grep dtoverlay /boot/config.txt && \
echo "" && \
echo "=== 4. DMESG CAMÉRA ===" && \
dmesg | grep -iE "imx|camera|csi|probe|failed|error" | head -50 && \
echo "" && \
echo "=== 5. VIDEO DEVICES ===" && \
ls -la /sys/class/video4linux/ && \
echo "" && \
echo "=== 6. I2C BUSES ===" && \
i2cdetect -l && \
echo "" && \
echo "=== 7. I2C DEVICES ===" && \
i2cdetect -y 2 2>/dev/null || i2cdetect -y 0 2>/dev/null
```

---

## 🚨 PROBLÈMES COURANTS ET SOLUTIONS

### Problème A: "No imx477.dtbo"
```
Cause: Overlay pas compilé ou pas inclus dans l'image
Solution: Recompiler avec dtbo inclus
```

### Problème B: "CSI is disabled"  
```
Cause: Firmware RPi ne supporte pas CSI sur ce pin
Solution: Vérifier câble CSI, essayer l'autre port (CSI0 vs CSI1)
```

### Problème C: "probe failed at address 0x10"
```
Cause: Caméra pas détectée sur I2C
Solution: Caméra défectueuse OU mal connectée
```

### Problème D: "DTB not found"
```
Cause: Device tree blob manquant
Solution: Vérifier /boot/overlays/ contient imx477.dtbo
```

---

## 📋 RAPPORTEZ-MOI:

Après avoir exécuté le diagnostic complet, dites-moi:

1. **CSI est "okay"?**
2. **imx477.dtbo existe?**
3. **dtoverlay=imx477 dans config.txt?**
4. **Erreurs dmesg pour imx477?**
5. **i2cdetect montre une caméra à 0x10?**
6. **TOUS les outputs du diagnostic**

Cela m'aidera à trouver la vraie cause! 🎯
