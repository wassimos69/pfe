# Services Lancés - RPi5 Minimal Image

## 🔧 Services Systemd Activés (4)

| # | Service | Description | État |
|----|---------|-------------|-------|
| 1 | `camera-module-init.service` | Initialisation caméra + modules kernel | Active |
| 2 | `wpa_supplicant@wlan0.service` | Gestion WiFi (WPA/WPA2) | Active |
| 3 | `systemd-networkd.service` | Configuration réseau DHCP | Active |
| 4 | `rpi-rootfs-autogrow.service` | Expansion partition /root au boot | Active (une fois) |

---

## 🎬 Services core-image-minimal (systemd intégrés)

| # | Service | Description |
|----|---------|-------------|
| 5 | `sshd.socket` | SSH serveur (port 22) |
| 6 | `systemd-udevd.service` | Gestion des périphériques |
| 7 | `systemd-logind.service` | Gestion sessions/utilisateurs |
| 8 | `systemd-tmpfiles-setup.service` | Création fichiers temporaires |
| 9 | `systemd-sysctl.service` | Application paramètres kernel |
| 10 | `systemd-journal-flush.service` | Logs système |

---

## 📦 Modules Kernel Auto-loadés (15 modules)

### Caméra & Pipeline vidéo (6)
| # | Module | Fonction |
|----|--------|----------|
| 11 | `imx477` | Capteur caméra Sony IMX477 |
| 12 | `rp1_cfe` | Frontend CSI-2 (Raspberry Pi) |
| 13 | `pisp_be` | Pipeline ISP backend |
| 14 | `v4l2_async` | Cadre asynchrone V4L2 |
| 15 | `v4l2_cci` | Interface CCI caméra |
| 16 | `v4l2_fwnode` | Support firmware V4L2 |

### Framework vidéo (5)
| # | Module | Fonction |
|----|--------|----------|
| 17 | `v4l2_mem2mem` | Processeur mémoire-vers-mémoire |
| 18 | `videobuf2_common` | Buffer vidéo commun |
| 19 | `videobuf2_dma_contig` | Buffer vidéo DMA contiguë |
| 20 | `videobuf2_memops` | Opérations mémoire buffers |
| 21 | `videobuf2_v4l2` | Interface V4L2 buffers |

### WiFi & Réseau (4)
| # | Module | Fonction |
|----|--------|----------|
| 22 | `brcmfmac` | Driver firmware Broadcom WiFi |
| 23 | `brcmutil` | Utilitaires Broadcom |
| 24 | `cfg80211` | Configuration wireless |
| 25 | `rfkill` | Contrôle RF (radio kill switch) |

---

## 📊 Résumé

```
✅ Services systemd:        4 unités
✅ Services core-image:     6+ services intégrés  
✅ Modules kernel:          15 modules auto-chargés
✅ Modules I2C:             3 (designware-core, designware-platform, i2c-dev)
✅ Support ventilateurs:    2 (pwm_fan, gpio_fan)

💾 TOTAL: 30+ composants actifs au boot
⚡ Tous chargés en parallèle via systemd
```

---

## 🚀 Démarrage typique

```
[Temps]    [Événement]
0.000s     Kernel start
3.226s     systemd initialization
3.500s     Module I2C + GPIO chargés
4.000s     wpa_supplicant démarrage
4.500s     systemd-networkd démarrage
7.000s     camera-module-init probe
8.500s     Tous drivers présents
10.100s    SSH prêt (sshd socket)
10.300s    Login prompt ✅
```

---

## 📥 Configuration réseau au boot

### Interfaces auto-configurées
```
wlan0   → DHCP via 25-wireless.network (timeout: 5s)
eth0    → DHCP via 20-wired.network (timeout: illimité)
```

### Services de fond
```
systemd-networkd    → Gestion automatique DHCP
wpa_supplicant      → Authentification WiFi
systemd-logind      → Sessions utilisateur
```

---

## 🔍 Vérification sur le hardware

Pour voir la liste complète des services actifs :
```bash
systemctl list-units --type=service --all
systemctl list-unit-files | grep enabled
lsmod | sort
```

Pour voir les services au démarrage :
```bash
systemd-analyze
systemd-analyze blame        # Services les plus lents
systemd-analyze critical-chain
```

---

*Documentation générée: April 2, 2026*
