"""
Script pour télécharger et préparer un dataset de détection de feux de forêt.
Utilise le dataset Ultralytics COCO8 pour les tests puis le dataset fire-satellite pour l'entraînement réel.
"""

import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

# Dataset paths
DATASETS_DIR = Path(__file__).parent.parent / "datasets"
YOLO_DIR = DATASETS_DIR / "yolo"

def download_ultralytics_fire_dataset():
    """
    Télécharge le dataset fire-detection d'Ultralytics Hub ou utilise 
    un dataset satellite fire disponible publiquement.
    """
    print("🔥 Préparation du dataset de détection de feux...")
    
    # Créer les dossiers
    for split in ["train", "val"]:
        (YOLO_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (YOLO_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)
    
    # Option 1: Utiliser le dataset coco8 pour test rapide (intégré à ultralytics)
    try:
        from ultralytics import YOLO
        from ultralytics.utils.downloads import download
        
        # Télécharger un dataset fire detection depuis HuggingFace/Roboflow
        # Dataset: wildfire smoke detection
        fire_dataset_url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco8.zip"
        
        # D'abord, testons avec COCO8 (dataset minimal pour validation du pipeline)
        print("📦 Téléchargement du dataset de test COCO8...")
        download(fire_dataset_url, dir=str(DATASETS_DIR))
        
        # Extraire
        zip_path = DATASETS_DIR / "coco8.zip"
        if zip_path.exists():
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(DATASETS_DIR)
            zip_path.unlink()
            print("✅ Dataset COCO8 extrait")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

def create_fire_dataset_yaml():
    """Crée le fichier dataset.yaml pour l'entraînement YOLO."""
    
    # Vérifier si on a COCO8 ou un autre dataset
    coco8_path = DATASETS_DIR / "coco8"
    
    if coco8_path.exists():
        # Utiliser COCO8 pour le test
        yaml_content = f"""# Ultralytics YOLO - Fire Detection Dataset
# Pour le prototype, on utilise COCO8

path: {coco8_path.as_posix()}
train: images/train
val: images/val

# Classes - COCO8 a 80 classes, on simule la détection de feux
names:
  0: person
  1: bicycle
  2: car
  3: motorcycle
  4: airplane
  5: bus
  6: train
  7: truck
  8: boat
  9: traffic light
  10: fire hydrant
  11: stop sign
  12: parking meter
  13: bench
  14: bird
  15: cat
  16: dog
  17: horse
  18: sheep
  19: cow
  20: elephant
  21: bear
  22: zebra
  23: giraffe
  24: backpack
  25: umbrella
  26: handbag
  27: tie
  28: suitcase
  29: frisbee
  30: skis
  31: snowboard
  32: sports ball
  33: kite
  34: baseball bat
  35: baseball glove
  36: skateboard
  37: surfboard
  38: tennis racket
  39: bottle
  40: wine glass
  41: cup
  42: fork
  43: knife
  44: spoon
  45: bowl
  46: banana
  47: apple
  48: sandwich
  49: orange
  50: broccoli
  51: carrot
  52: hot dog
  53: pizza
  54: donut
  55: cake
  56: chair
  57: couch
  58: potted plant
  59: bed
  60: dining table
  61: toilet
  62: tv
  63: laptop
  64: mouse
  65: remote
  66: keyboard
  67: cell phone
  68: microwave
  69: oven
  70: toaster
  71: sink
  72: refrigerator
  73: book
  74: clock
  75: vase
  76: scissors
  77: teddy bear
  78: hair drier
  79: toothbrush
"""
    else:
        # Dataset fire detection personnalisé
        yaml_content = f"""# EDGE SPACE - Fire Detection Dataset
path: {YOLO_DIR.as_posix()}
train: images/train
val: images/val

# Classes pour détection de feux de forêt
names:
  0: fire
  1: smoke
"""
    
    yaml_path = DATASETS_DIR / "dataset.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"✅ Fichier dataset.yaml créé: {yaml_path}")
    return yaml_path

def download_real_fire_dataset():
    """
    Télécharge un vrai dataset de détection de feux.
    Utilise le dataset 'D-Fire' ou 'fire-smoke-dataset' de Roboflow Universe.
    """
    print("\n🔥 Téléchargement du dataset D-Fire (détection feux/fumée)...")
    
    try:
        # Dataset D-Fire - format YOLO directement
        # https://github.com/gaiasd/DFireDataset
        dfire_url = "https://github.com/gaiasd/DFireDataset/releases/download/v1.0/D-Fire.zip"
        
        zip_path = DATASETS_DIR / "D-Fire.zip"
        dfire_dir = DATASETS_DIR / "D-Fire"
        
        if not dfire_dir.exists():
            print(f"📥 Téléchargement depuis {dfire_url}...")
            urllib.request.urlretrieve(dfire_url, zip_path)
            
            print("📂 Extraction du dataset...")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(DATASETS_DIR)
            
            zip_path.unlink()
            print("✅ Dataset D-Fire téléchargé et extrait!")
        else:
            print("✅ Dataset D-Fire déjà présent")
        
        # Créer le fichier YAML pour D-Fire
        yaml_content = f"""# D-Fire Dataset - Fire and Smoke Detection
# https://github.com/gaiasd/DFireDataset

path: {dfire_dir.as_posix()}
train: train/images
val: test/images

# Classes
names:
  0: fire
  1: smoke
"""
        yaml_path = DATASETS_DIR / "dfire.yaml"
        yaml_path.write_text(yaml_content, encoding="utf-8")
        print(f"✅ Fichier dfire.yaml créé: {yaml_path}")
        
        return yaml_path
        
    except Exception as e:
        print(f"❌ Erreur téléchargement D-Fire: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("EDGE SPACE - Préparation des datasets")
    print("=" * 60)
    
    # Télécharger D-Fire (dataset feux réel)
    dfire_yaml = download_real_fire_dataset()
    
    # Télécharger aussi COCO8 pour les tests rapides
    download_ultralytics_fire_dataset()
    create_fire_dataset_yaml()
    
    print("\n" + "=" * 60)
    print("✅ Datasets prêts!")
    if dfire_yaml:
        print(f"   Dataset principal: {dfire_yaml}")
    print("=" * 60)
