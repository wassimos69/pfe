# 📖 Guide Complet - Diagnostic et Correction Caméra RPi5

## 🎯 Situation Actuelle

- Image compilée et flashée sur RPi5
- libcamera détecte ZÉRO caméra
- Modules kernel possiblement pas chargés
- Besoin diagnostic directe sur le device

---

## 📚 Documents Créés

1. **ACTION_PLAN.md** ← **COMMENCEZ PAR CELUI-CI** 🚀
   - Plan étape par étape  
   - Commande de diagnostic unique
   - Ce qu'il faut rapporter

2. **DEBUG_CAMERA_UART.md**
   - Guide détaillé du diagnostic via UART
   - 11 tests progressifs
   - Hypothèses de causes

3. **CORRECTIONS_GUIDE.md**  
   - Solutions pour chaque scénario d'erreur
   - Code des corrections à appliquer
   - Commandes de recompilation

4. **CAMERA_DIAGNOSTIC.md**
   - Diagnostic ancien (gardé pour référence)

5. **CAMERA_TEST_GUIDE.md**
   - Tests que libcamera devrait passer

6. **DEPLOY_FIXED_IMAGE.md**
   - Déploiement de l'image

---

## ⚡ Fluxo Rapide (TL;DR)

### 1️⃣ Connectez-vous au Pi
```bash
sudo picocom -b 115200 /dev/ttyUSB0
# root / root
```

### 2️⃣ Exécutez le diagnostic
```bash
modprobe imx477 && modprobe bcm2835_unicam && modprobe rp1_cfe && \
lsmod | grep -E "imx477|unicam|cfe" && \
ls /dev/video* && \
dmesg | tail -30 | grep -iE "imx|csi|error" && \
grep dtoverlay /boot/config.txt && \
timeout 3 libcamera-hello --list-cameras
```

### 3️⃣ Rapportez les résultats
Copiez-collez **TOUT** et dites-moi:
- Modules OK ou FAIL?
- /dev/video* existe?
- Erreurs dans dmesg?
- dtoverlay=imx477 dans config.txt?
- Résultat libcamera?

### 4️⃣ J'applique la correction
Je vous dis exactement quel fichier éditer et comment recompiler

### 5️⃣ Flash et test!

---

## 🔧 Fichiers Clés du Projet

```
layers/meta-football/
├── recipes-core/images/
│   └── rpi5-minimal.bb
│       └── KERNEL_MODULE_AUTOLOAD (peut nécessiter ajustement)
│
├── recipes-bsp/bootfiles/
│   └── rpi-config_git.bbappend
│       └── RPI_EXTRA_CONFIG (dtoverlay=imx477)
│
└── recipes-multimedia/libcamera/
    └── libcamera_0.4.0.bbappend
        └── LIBCAMERA_PIPELINES (pipeline RPi forcé)
```

---

## 📊 Résultats Attendus (Succès)

```bash
root@raspberrypi5:~# libcamera-hello --list-cameras
Available cameras
0 : imx477 [4608x3456] (/base/axi/pcie@120000/rp1/csi@800000/csi-bridge@0)
```

---

## 🚀 PROCHAINES ÉTAPES

1. **Lisez** `ACTION_PLAN.md`
2. **Exécutez** le diagnostic sur le Pi
3. **Rapportez** les résultats **EXACTEMENT**
4. **Partagez** les erreurs/logs de dmesg
5. **Je fournirai** la correction précise

---

## 🆘 Support Immédiat

Pendant que vous faites le diagnostic, je peux:
- ✅ Analyser les résultats dmesg
- ✅ Écrire les corrections de bbappend
- ✅ Compiler l'image corrigée
- ✅ Vous guider étape par étape

**Attendez juste vos résultats de diagnostic!** 🎯

---

## 📝 Checklist

- [ ] J'ai lu ACTION_PLAN.md
- [ ] J'ai se connecté au Pi via picocom
- [ ] J'ai exécuté le diagnostic
- [ ] J'ai copié TOUS les résultats
- [ ] Je rapporte les résultats complets

Je suis prêt quand vous l'êtes! 🚀
