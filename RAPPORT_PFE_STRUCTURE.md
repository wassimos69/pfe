# Rapport de Projet de Fin d'Études (PFE)
## Intégration d'un Système de Détection Multimodèle avec Accélérateur Hailo8L sur Raspberry Pi

---

## Table des matières
1. [Introduction](#introduction)
2. [État de l'Art et Contexte](#état-de-lart-et-contexte)
3. [Objectifs et Enjeux](#objectifs-et-enjeux)
4. [Architecture Générale du Système](#architecture-générale-du-système)
5. [Implémentation](#implémentation)
6. [Tests et Résultats](#tests-et-résultats)
7. [Conclusion et Perspectives](#conclusion-et-perspectives)
8. [Références](#références)

---

## 1. Introduction {#introduction}

### 1.1 Contexte Général
- Évolution vers l'Edge AI et l'inference locale
- Besoin croissant de systèmes de détection embarqués temps réel
- Contraintes : puissance limitée, latence faible, coûts réduits

### 1.2 Présentation du Projet
Brief description du projet:
- Plateforme: Raspberry Pi 4/5
- Accélérateur IA: Hailo8L
- Système d'exploitation embarqué: Yocto Linux
- Application: Système de détection multimodèle avec transmission serveur

### 1.3 Motivation et Utilité
- Démonstration d'une solution viable pour l'Edge AI industriel
- Intégration complète d'une pile logicielle optimisée
- Cas d'usage : surveillance, détection d'anomalies, analyse vidéo temps réel

---

## 2. État de l'Art et Contexte {#état-de-lart-et-contexte}

### 2.1 Systèmes de Détection d'Objets
#### 2.1.1 Modèles Populaires
- **YOLO (You Only Look Once)**: architecture, versions, performances
- **SSD (Single Shot MultiBox Detector)**: forces et faiblesses
- **RetinaNet, EfficientDet**: autres alternatives

#### 2.1.2 Métriques de Performance
- Précision (mAP)
- Rappel
- Vitesse d'inférence (FPS)
- Consommation mémoire/puissance

### 2.2 Accélérateurs Matériels pour l'IA
#### 2.2.1 Comparaison des Solutions
- **GPU (NVIDIA Jetson)**: performances, consommation
- **TPU (Google)**: disponibilité, coûts
- **Hailo**: approche spécialisée, avantages pour quantization

#### 2.2.2 Hailo8L - Caractéristiques
- Architecture et capacités
- Support modèles (YOLO, SSD, etc.)
- Consommation énergétique
- Intégration Yocto existante

### 2.3 Systèmes d'Exploitation Embarqués
#### 2.3.1 Alternatives
- Raspberry Pi OS (débuts rapides, flexibilité limitée)
- Yocto: avantages pour systèmes custom
- Buildroot: simplicité vs fonctionnalités

#### 2.3.2 Yocto pour Systèmes Edge
- Build custom minimal
- Support Hailo8L (meta-hailo)
- Optimisation taille/performance

### 2.4 Architecture Client-Serveur pour Détection
- Patterns de transmission de données
- Sérialisation (JSON, Protocol Buffers)
- Protocoles (HTTP/REST, MQTT, gRPC)
- Latence et bande passante

---

## 3. Objectifs et Enjeux {#objectifs-et-enjeux}

### 3.1 Objectifs Généraux
- [ ] Construire une image Yocto optimisée pour Raspberry Pi + Hailo8L
- [ ] Intégrer deux modèles de détection dans le système
- [ ] Développer pipeline de détection temps réel
- [ ] Implémenter transmission serveur des résultats
- [ ] Valider performances et latences

### 3.2 Objectifs Spécifiques
#### 3.2.1 Système Yocto
- Intégrer les couches Hailo (meta-hailo)
- Compiler driver/runtime Hailo
- Optimiser taille image
- Déploiement sur Raspberry Pi

#### 3.2.2 Modèles de Détection
- Conversion / quantization pour Hailo
- Déploiement deux modèles parallèles ou séquentiels
- Calibration et optimisation
- Gestion mémoire

#### 3.2.3 Pipeline d'Inference
- Capture source vidéo/images
- Preprocessing
- Inference avec Hailo
- Post-processing et décision
- Serialization des résultats

#### 3.2.4 Communication Serveur
- API REST/REST ou MQTT
- Format données (JSON)
- Gestion connexion
- Logging résultats

### 3.3 Contraintes et Défis
- **Performance**: ~30 FPS avec deux modèles
- **Latence**: <100ms analyse + transmission
- **Mémoire**: <500MB pour application
- **Connectivité**: WiFi/Ethernet fiable
- **Coûts**: BOM < $XXX

---

## 4. Architecture Générale du Système {#architecture-générale-du-système}

### 4.1 Schéma Architectural Global
```
┌─────────────────────────────────────────────────────────────┐
│                    Systèmes Externes                         │
│  • Caméra / Source Vidéo                                    │
│  • Serveur Backend (stockage + visualisation)               │
└─────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 4/5                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Système d'Exploitation Yocto                  │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │   Application de Détection (Python/C++)         │ │ │
│  │  │                                                  │ │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │ │ │
│  │  │  │ Capture  │→ │ Pipeline │→ │ Modèles  │      │ │ │
│  │  │  │ Vidéo    │  │ Prepro   │  │ Détection│      │ │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │ │ │
│  │  │         ↓                          ↓             │ │ │
│  │  │    ┌────────────────────────┐                   │ │ │
│  │  │    │  Runtime Hailo         │                   │ │ │
│  │  │    │  (hailort + driver)    │                   │ │ │
│  │  │    └────────────────────────┘                   │ │ │
│  │  │         ↓                                        │ │ │
│  │  │    ┌──────────────┐   ┌──────────────┐         │ │ │
│  │  │    │ Post-Process │→  │ Transmission │         │ │ │
│  │  │    │ & Décision   │   │ Serveur      │         │ │ │
│  │  │    └──────────────┘   └──────────────┘         │ │ │
│  │  │                             ↓                   │ │ │
│  │  └─────────────────────────────┼──────────────────┘ │ │
│  │                                 │                    │ │
│  │  ┌──────────────────────────────┼──────────────────┐ │ │
│  │  │  Drivers et Services Système                   │ │ │
│  │  │  • Hailo driver                                │ │ │
│  │  │  • Camera interface                            │ │ │
│  │  │  • Network stack                               │ │ │
│  │  │  • Storage                                     │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    Matériel Hailo8L (USB / PCIe)                    │   │
│  │    • Accélérateur IA spécialisé                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ↓
          ┌──────────────────────────────────┐
          │  Serveur Backend                 │
          │  • Base de données               │
          │  • API REST                      │
          │  • Dashboard visualisation       │
          └──────────────────────────────────┘
```

### 4.2 Couches Logicielles

#### 4.2.1 Couche 1: Système d'Exploitation (Yocto)
- Buildroot Yocto optimisé
- Kernel Linux patché pour Hailo
- Drivers périphériques (camera, network)
- Services système (systemd)

#### 4.2.2 Couche 2: Runtime IA (Hailo)
- Hailo hardware driver
- Hailort (Hailo Runtime)
- Bindings Python/C++
- Resource management

#### 4.2.3 Couche 3: Pipeline d'Inference
- **Module Capture**: V4L2, GStreamer ou camera spécifique
- **Module Preprocessing**: redimensionnement, normalisation
- **Module Inference**: Hailo API appels
- **Module Post-processing**: parsing résultats, NMS

#### 4.2.4 Couche 4: Application Applicative
- Orchestration des modèles
- Logique de détection
- Sérialisation résultats
- Communication serveur

### 4.3 Flux de Données

1. **Acquisition** → Caméra/USB → Buffer vidéo
2. **Preprocessing** → Resize, normalize, format Hailo
3. **Inference** → Hailo8L → sorties brutes [probs, bboxes]
4. **Post-processing** → NMS, filtering, labelling
5. **Sérialisation** → JSON avec détections
6. **Transmission** → HTTP POST vers serveur
7. **Logging** → Base données serveur

---

## 5. Implémentation {#implémentation}

### 5.1 Environnement de Développement

#### 5.1.1 Outils Requis
- Yocto: bitbake, OE-core
- Cross-compiler ARM
- Hailo SDK et quantization tools
- Python 3.x avec HailoRT bindings
- Git pour versionning

#### 5.1.2 Matériel
- Raspberry Pi 4/5
- Hailo8L (USB 3.0 ou PCIe)
- Caméra compatible (CSI ou USB)
- Carte SD/eMMC 64GB+ (build artifacts)
- Réseau (WiFi ou Ethernet)

### 5.2 Construction de l'Image Yocto

#### 5.2.1 Préparation des Couches
```bash
# Structure attendue
yocto/
├── poky/                    # OE-core principal
├── meta-raspberrypi/        # Support Raspberry Pi
├── meta-hailo/              # Support Hailo8L
├── meta-openembedded/       # Paquets additionnels
└── meta-football/           # Custom layers (si nécessaire)
```

#### 5.2.2 Configuration bblayers.conf
- Inclure meta-raspberrypi
- Inclure meta-hailo
- Vérifier MACHINE = "raspberrypi4" ou "raspberrypi5"

#### 5.2.3 Configuration local.conf
- IMAGE_INSTALL += "hailort python3-hailo"
- Optimisations: CPU_FLAGS, taille minimal
- DISTRO features: camera, networking

#### 5.2.4 Recette personnalisée (meta-football)
- Recipe pour application détection
- Dépendances: hailort, opencv (ou slim), gstreamer
- Packaging et installation

#### 5.2.5 Build Command
```bash
bitbake core-image-minimal  # ou custom image
```

### 5.3 Modèles de Détection

#### 5.3.1 Sélection des Modèles
- **Modèle 1**: [nom et source]
  - Architecture: YOLO/SSD/RetinaNet
  - Entrée: [dimensions]
  - Classes détectées: [liste]
  - FPS attendu solo: ~X FPS

- **Modèle 2**: [nom et source]
  - Architecture: [type]
  - Entrée: [dimensions]
  - Classes détectées: [liste]
  - FPS attendu solo: ~Y FPS

#### 5.3.2 Conversion et Quantization
- Format original: ONNX / TensorFlow / PyTorch
- Outil Hailo: Hailo Model Zoo ou Custom quantization
- Post-training quantization (PTQ)
- Calibration dataset: [description]

#### 5.3.3 Déploiement des Modèles
```
Models/
├── model_detection_1.hef    # Format Hailo compilé
└── model_detection_2.hef
```

### 5.4 Pipeline d'Application

#### 5.4.1 Capture Vidéo
```python
# Pseudocode
capture = init_camera()  # V4L2 ou GStreamer
while True:
    frame = capture.read()
    # pipeline...
```

#### 5.4.2 Preprocessing
```python
# Redimensionner à input size du modèle
frame_resized = resize(frame, (480, 480))
# Normaliser
frame_normalized = normalize(frame_resized, mean, std)
```

#### 5.4.3 Inference Twin Models
```python
# Option A: Séquentiel
results1 = infer_model1(frame)
results2 = infer_model2(frame)

# Option B: Parallèle (si ressources)
results1_async = infer_model1_async(frame)
results2_async = infer_model2_async(frame)
results1 = wait(results1_async)
results2 = wait(results2_async)
```

#### 5.4.4 Post-processing
```python
# Parse outputs
detections = []
for model_output in [results1, results2]:
    for detection in parse_output(model_output):
        detections.append({
            'model': model_id,
            'class': detection.class_id,
            'confidence': detection.confidence,
            'bbox': detection.bbox,
            'timestamp': time.time()
        })

# NMS if combined
detections = nms(detections)
```

#### 5.4.5 Sérialisation et Transmission
```python
# Sérialiser résultats
payload = {
    'timestamp': time.time(),
    'device_id': 'raspi_001',
    'detections': detections,
    'frame_id': frame_count
}

# Envoyer au serveur
response = requests.post(
    'http://server/api/detections',
    json=payload,
    timeout=5
)
```

### 5.5 Structure de Code Recommandée

```
/home/app/
├── inference/
│   ├── __init__.py
│   ├── camera.py          # Capture vidéo
│   ├── models.py          # Charge modèles Hailo
│   ├── preprocessing.py   # Preprocessing frames
│   ├── pipeline.py        # Pipeline principal
│   └── postprocess.py     # Post-processing résultats
├── server/
│   ├── __init__.py
│   ├── client.py          # Client HTTP/REST
│   └── config.py          # URLs, authentification
├── utils/
│   ├── __init__.py
│   ├── logger.py          # Logging
│   └── metrics.py         # FPS, latence
├── configs/
│   ├── models.json        # Chemins modèles
│   ├── server.json        # Endpoints serveur
│   └── inference.json     # Params inference
├── main.py                # Point d'entrée
└── requirements.txt       # Dépendances Python
```

### 5.6 Serveur Backend

#### 5.6.1 API REST (exemple FastAPI/Flask)
```python
@app.post("/api/detections")
def receive_detections(data: DetectionPayload):
    # Valider
    # Stocker en BD
    # Logger
    # Renvoyer confirmation
    return {"status": "received", "id": result_id}
```

#### 5.6.2 Base de Données
- Schéma: timestamp, device_id, detections (JSON), confidence_stats
- Index: timestamp, device_id
- Retention: politique archivage

#### 5.6.3 Dashboard
- Affichage temps réel détections
- Graphiques statistiques
- Export rapports

---

## 6. Tests et Résultats {#tests-et-résultats}

### 6.1 Plan de Tests

#### 6.1.1 Tests Unitaires
- [ ] Parsing sorties modèles Hailo
- [ ] NMS algorithme
- [ ] Sérialisation JSON
- [ ] Communication serveur (retry, timeout)

#### 6.1.2 Tests d'Intégration
- [ ] Pipeline complet mono-modèle
- [ ] Deux modèles parallèles
- [ ] Transmission serveur async
- [ ] Récupération d'erreurs

#### 6.1.3 Tests de Performance
- [ ] FPS avec un modèle
- [ ] FPS avec deux modèles
- [ ] Latence E2E (frame → serveur)
- [ ] Utilisation CPU/GPU/Memory
- [ ] Consommation énergétique

#### 6.1.4 Tests de Fiabilité
- [ ] Stabilité 24h
- [ ] Reconnexion serveur
- [ ] USB Hailo disconnect/reconnect
- [ ] Handle frames perdues

### 6.2 Résultats Attendus

| Métrique | Cible | Résultat |
|----------|-------|----------|
| FPS (1 modèle) | 30+ | ? |
| FPS (2 modèles) | 15+ | ? |
| Latence E2E | <150ms | ? |
| Précision (mAP) | TBD | ? |
| Mémoire RAM usage | <500MB | ? |
| Débit réseau | <10Mbps | ? |
| Uptime 24h | 99%+ | ? |

### 6.3 Benchmarking

- Dataset de test: [description]
- Méthodes évaluation: confusion matrix, metrics
- Comparaison vs GPU (si applicable)
- ROI et TCO

---

## 7. Conclusion et Perspectives {#conclusion-et-perspectives}

### 7.1 Résumé Achievements
- ✓ Image Yocto build réussie
- ✓ Hailo8L intégré et fonctionnel
- ✓ Deux modèles détection opérationnels
- ✓ Pipeline temps réel validé
- ✓ Communication serveur stable

### 7.2 Limitations Rencontrées
- [Limite 1]
- [Limite 2]
- Solutions palliatives

### 7.3 Améliorations Futures
1. **Court terme**
   - Optimisation latence réseau
   - Ajouter modèle 3e (si ressources)
   - Dashboard avancée

2. **Moyen terme**
   - Intégration cloud (AWS/GCP)
   - Machine learning offline
   - Améliorer quantization

3. **Long terme**
   - Déploiement production
   - Scaling multi-devices
   - Edge computing distribué

### 7.4 Recommandations
- Pour déploiement industriel: [recommandation]
- Pour recherche future: [piste]

---

## 8. Références {#références}

### Documentation Officielle
- [Hailo8L Datasheet](https://www.hailo.ai/)
- [Hailo Model Zoo](https://github.com/hailo-ai/)
- [Yocto Project Manual](https://docs.yoctoproject.org/)
- [Raspberry Pi Docs](https://www.raspberrypi.com/documentation/)

### Papers et Articles
- YOLO: Real-Time Object Detection
- SSD: Single Shot MultiBox Detector
- SqueezeNet: Efficient Networks

### Ressources
- Meta-Hailo Layer: [URL/repo]
- ONNX Runtime
- GStreamer Documentation

---

## Annexes (optionnel)

### A. Schémas Détaillés
### B. Code Source Complet
### C. Scripts Build
### D. Configuration Fichiers
### E. Résultats Tests Détaillés
### F. Photos/Vidéos Système

---

**Document créé**: [Date]  
**Auteur**: [Nom]  
**Affiliation**: [École/Entreprise]  
**Version**: 1.0 - Draft
