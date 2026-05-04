# 🎯 DIAGNOSTIC CAMÉRA - EXPLIQUÉ SIMPLEMENT

## Ce qu'on cherche

Pourquoi libcamera dit "no cameras available" alors qu'on devrait avoir une caméra?

---

## Le Plan (en français)

### Étape 1: Ouvrir la connexion au Pi
```bash
sudo picocom -b 115200 /dev/ttyUSB0
# Tapez: root
# Tapez: root
```

### Étape 2: Tester si les modules kernel sont présents

**C'est quoi?** Les modules kernel sont des pilotes logiciels pour la caméra.
**Pourquoi?** Si les modules ne sont pas chargés, la caméra ne peut pas du tout être utilisée.

Sur le Pi, tapez:
```bash
modprobe imx477
modprobe bcm2835_unicam
modprobe rp1_cfe
```

Ces commandes **chargent** les modules. Si c'est OK, vous ne verrez pas d'erreurs.

### Étape 3: Vérifier que c'est chargé

```bash
lsmod | grep imx477
```

Vous devriez voir quelque chose comme:
```
imx477                 24576  0
```

Si rien n'affiche = LES MODULES NE SONT PAS CHARGÉS. C'est un problème!

### Étape 4: Vérifier si la caméra est visible au système

```bash
ls /dev/video*
```

Vous devriez voir:
```
/dev/video0  /dev/video1
```

Si rien d'affiche = LA CAMÉRA N'EST PAS DÉTECTÉE. C'est un problème!

### Étape 5: Voir les erreurs du kernel

```bash
dmesg | tail -50
```

Cherchez des lignes avec:
- `imx477` 
- `CSI`
- `camera`
- `error`
- `failed`

Si vous voyez "CSI disabled" ou "imx477 not found" = C'EST L'ERREUR!

### Étape 6: Vérifier la configuration de boot

```bash
cat /boot/config.txt | grep dtoverlay
```

Vous DEVEZ voir:
```
dtoverlay=imx477
```

Si rien = LA CONFIGURATION EST MANQUANTE!

### Étape 7: Tester libcamera

```bash
libcamera-hello --list-cameras
```

**Si libcamera trouve la caméra, vous verrez:**
```
Available cameras
0 : imx477 [4608x3456]
```

**Si libcamera ne la voit pas:**
```
ERROR: *** no cameras available ***
```

---

## Résumé: Quels Résultats Rapporter?

Après avoir exécuté tout ça, dites-moi:

1. **Modules kernel:** 
   - La commande `lsmod | grep imx477` affiche quelque chose? OUI/NON

2. **/dev/video**
   - La commande `ls /dev/video*` affiche quelque chose? OUI/NON

3. **Erreurs dmesg**
   - La commande `dmesg | tail -50` affiche des erreurs? OUI/NON
   - Si OUI, copier-collez les 5-10 lignes avec erreurs

4. **Config dtoverlay**
   - La commande `grep dtoverlay /boot/config.txt` affiche "imx477"? OUI/NON

5. **Résultat libcamera**
   - Copier-collez EXACTEMENT ce qu'affiche `libcamera-hello --list-cameras`

---

## Cas Courants

### Cas 1: Modules OK, /dev/video OK, mais libcamera Fail
→ **Problème libcamera lui-même**
→ Je dois recompi ler libcamera

### Cas 2: Modules FAIL (erreur quand vous tapez modprobe)
→ **Les modules ne sont pas compilés**
→ Je dois recompiler le kernel

### Cas 3: /dev/video absent même après modprobe OK
→ **La caméra n'est pas détectée par le système**
→ Vérifier le câble CSI ou la configuration

### Cas 4: dmesg plein d'erreurs "CSI disabled"
→ **Le firmware RPi dit que CSI est désactivé**
→ Je dois modifier config.txt

---

## La Commande Ultra-Simple

Si vous voulez TOUT en une seule commande, tapez CECI sur le Pi:

```bash
modprobe imx477 && modprobe bcm2835_unicam && modprobe rp1_cfe && echo "OK" && lsmod | grep imx477 && ls /dev/video* && dmesg | tail -30 && cat /boot/config.txt | grep dtoverlay && libcamera-hello --list-cameras
```

Puis copiez tout ce qui s'affiche et envoyez-le moi.

---

## Résumé Visuel

```
┌─────────────────────────────────────────────┐
│ Sur le Pi, exécutez:                        │
│                                             │
│ modprobe imx477                             │
│ modprobe bcm2835_unicam                     │
│ modprobe rp1_cfe                            │
│                                             │
│ (Pas d'erreur? OK!)                         │
│                                             │
│ lsmod | grep imx477                         │
│ (Affiche quelque chose? OK!)                │
│                                             │
│ ls /dev/video*                              │
│ (Affiche /dev/video0? OK!)                  │
│                                             │
│ libcamera-hello --list-cameras              │
│ (Affiche "0 : imx477"? OUI!)                │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Questions?

Rapportez-moi EXACTEMENT ce que vous voyez après chaque commande et je vous dis ce qu'il faut corriger! 🎯

C'est facile - attendez juste vos résultats! 🚀
