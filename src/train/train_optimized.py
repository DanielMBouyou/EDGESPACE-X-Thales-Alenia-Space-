"""
Script d'entraînement YOLO optimisé pour RTX 4050 (6GB VRAM)
Détection de feux de forêt via images satellites

Optimisations:
- YOLOv8/v11 avec les meilleurs hyperparamètres
- Mixed precision (FP16) pour économiser la VRAM
- Data augmentation avancée
- Early stopping et cosine annealing
- Export ONNX quantisé pour l'edge
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

import torch


def get_optimal_config(model_size: str = "s", vram_gb: float = 6.0):
    """
    Retourne la configuration optimale selon le GPU.
    RTX 4050 = 6GB VRAM → on optimise batch size et image size
    """
    
    # Configurations selon la taille du modèle et VRAM disponible
    configs = {
        "n": {  # nano - ultra rapide, léger
            "batch": 32 if vram_gb >= 6 else 16,
            "imgsz": 640,
            "workers": 8,
        },
        "s": {  # small - bon équilibre speed/accuracy
            "batch": 16 if vram_gb >= 6 else 8,
            "imgsz": 640,
            "workers": 8,
        },
        "m": {  # medium - meilleure accuracy
            "batch": 8 if vram_gb >= 6 else 4,
            "imgsz": 640,
            "workers": 4,
        },
        "l": {  # large - haute accuracy
            "batch": 4 if vram_gb >= 6 else 2,
            "imgsz": 640,
            "workers": 4,
        },
        "x": {  # extra large - max accuracy
            "batch": 2 if vram_gb >= 6 else 1,
            "imgsz": 640,
            "workers": 2,
        },
    }
    
    return configs.get(model_size, configs["s"])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Entraînement YOLO optimisé pour détection de feux"
    )
    p.add_argument(
        "--data", 
        default="datasets/dfire.yaml",
        help="Chemin vers le fichier dataset.yaml"
    )
    p.add_argument(
        "--model", 
        default="yolo11s.pt",  # YOLOv11 small par défaut (meilleur que v8)
        help="Modèle pré-entraîné (yolo11n/s/m/l/x.pt ou yolov8n/s/m/l/x.pt)"
    )
    p.add_argument(
        "--epochs", 
        type=int, 
        default=100,
        help="Nombre d'époques (100 recommandé pour bon résultat)"
    )
    p.add_argument(
        "--imgsz", 
        type=int, 
        default=640,
        help="Taille des images"
    )
    p.add_argument(
        "--batch", 
        type=int, 
        default=-1,  # Auto-batch
        help="Batch size (-1 pour auto)"
    )
    p.add_argument(
        "--patience", 
        type=int, 
        default=20,
        help="Early stopping patience"
    )
    p.add_argument(
        "--project", 
        default="runs",
        help="Dossier de sortie"
    )
    p.add_argument(
        "--name", 
        default=None,
        help="Nom de l'expérience (auto-généré si non spécifié)"
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Reprendre l'entraînement depuis le dernier checkpoint"
    )
    
    return p.parse_args()


def train(args: argparse.Namespace) -> dict:
    """Entraîne le modèle avec les optimisations pour RTX 4050."""
    
    from ultralytics import YOLO
    
    print("=" * 70)
    print("🔥 EDGE SPACE - Entraînement YOLO pour détection de feux de forêt")
    print("=" * 70)
    
    # Vérification GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🎮 GPU détecté: {gpu_name} ({vram:.1f} GB VRAM)")
    else:
        vram = 0
        print("⚠️  Pas de GPU CUDA détecté, entraînement sur CPU")
    
    # Charger le modèle
    print(f"\n📦 Chargement du modèle: {args.model}")
    model = YOLO(args.model)
    
    # Déterminer la taille du modèle (n/s/m/l/x)
    model_size = "s"  # défaut
    for size in ["n", "s", "m", "l", "x"]:
        if size in args.model.lower():
            model_size = size
            break
    
    # Configuration optimale
    config = get_optimal_config(model_size, vram)
    
    # Utiliser batch auto ou config optimale
    batch_size = args.batch if args.batch > 0 else config["batch"]
    
    # Nom de l'expérience
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_name = args.name or f"fire_detection_{model_size}_{timestamp}"
    
    print(f"\n⚙️  Configuration d'entraînement:")
    print(f"   • Dataset: {args.data}")
    print(f"   • Modèle: {args.model} (taille: {model_size})")
    print(f"   • Époques: {args.epochs}")
    print(f"   • Batch size: {batch_size}")
    print(f"   • Image size: {args.imgsz}x{args.imgsz}")
    print(f"   • Early stopping patience: {args.patience}")
    print(f"   • Expérience: {exp_name}")
    
    print("\n" + "=" * 70)
    print("🚀 Démarrage de l'entraînement...")
    print("=" * 70 + "\n")
    
    # ========================================
    # ENTRAÎNEMENT AVEC HYPERPARAMÈTRES OPTIMAUX
    # ========================================
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=batch_size,
        
        # === Optimisations GPU RTX 4050 ===
        device=0 if torch.cuda.is_available() else "cpu",
        workers=config["workers"],
        amp=True,  # Mixed precision (FP16) - économise VRAM
        cache=True,  # Cache images en RAM pour vitesse
        
        # === Scheduler & Optimizer ===
        optimizer="AdamW",  # Meilleur que SGD pour ce type de données
        lr0=0.001,  # Learning rate initial
        lrf=0.01,  # Learning rate final (cosine decay)
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        # === Early Stopping ===
        patience=args.patience,
        
        # === Data Augmentation avancée ===
        hsv_h=0.015,  # Hue augmentation
        hsv_s=0.7,    # Saturation augmentation
        hsv_v=0.4,    # Value augmentation
        degrees=10.0, # Rotation
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0001,
        flipud=0.5,   # Flip vertical (utile pour images satellite)
        fliplr=0.5,   # Flip horizontal
        mosaic=1.0,   # Mosaic augmentation (très efficace)
        mixup=0.1,    # Mixup augmentation
        copy_paste=0.1,  # Copy-paste augmentation
        
        # === Régularisation ===
        dropout=0.0,  # Pas de dropout pour YOLO (déjà régularisé)
        
        # === Output ===
        project=args.project,
        name=exp_name,
        exist_ok=True,
        pretrained=True,
        verbose=True,
        save=True,
        save_period=10,  # Sauvegarder checkpoint toutes les 10 époques
        plots=True,  # Générer les graphiques
        
        # === Validation ===
        val=True,
        split="val",
        
        # === Box loss ===
        box=7.5,  # Box loss gain
        cls=0.5,  # Class loss gain
        dfl=1.5,  # DFL loss gain
        
        # === Resume ===
        resume=args.resume,
    )
    
    # ========================================
    # POST-ENTRAÎNEMENT
    # ========================================
    
    save_dir = Path(model.trainer.save_dir)
    print("\n" + "=" * 70)
    print("✅ Entraînement terminé!")
    print("=" * 70)
    
    # Copier le meilleur modèle
    best_src = save_dir / "weights" / "best.pt"
    best_dst = Path("models/weights/best.pt")
    best_dst.parent.mkdir(parents=True, exist_ok=True)
    
    if best_src.exists():
        shutil.copy2(best_src, best_dst)
        print(f"\n📁 Meilleur modèle copié: {best_dst}")
    
    # Extraire les métriques finales
    summary = {}
    results_csv = save_dir / "results.csv"
    if results_csv.exists():
        lines = results_csv.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) >= 2:
            header = [h.strip() for h in lines[0].split(",")]
            last = [v.strip() for v in lines[-1].split(",")]
            row = dict(zip(header, last))
            summary = {
                "model": args.model,
                "epochs_trained": len(lines) - 1,
                "precision": float(row.get("metrics/precision(B)", 0.0)),
                "recall": float(row.get("metrics/recall(B)", 0.0)),
                "mAP50": float(row.get("metrics/mAP50(B)", 0.0)),
                "mAP50-95": float(row.get("metrics/mAP50-95(B)", 0.0)),
                "train_box_loss": float(row.get("train/box_loss", 0.0)),
                "train_cls_loss": float(row.get("train/cls_loss", 0.0)),
                "val_box_loss": float(row.get("val/box_loss", 0.0)),
                "val_cls_loss": float(row.get("val/cls_loss", 0.0)),
            }
    
    # Sauvegarder le résumé
    summary["experiment"] = exp_name
    summary["save_dir"] = str(save_dir)
    summary["weights"] = str(best_dst)
    
    summary_path = Path("runs/summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print(f"\n📊 Métriques finales:")
    print(f"   • Precision: {summary.get('precision', 0):.4f}")
    print(f"   • Recall: {summary.get('recall', 0):.4f}")
    print(f"   • mAP@50: {summary.get('mAP50', 0):.4f}")
    print(f"   • mAP@50-95: {summary.get('mAP50-95', 0):.4f}")
    
    print(f"\n📁 Fichiers sauvegardés:")
    print(f"   • Modèle: {best_dst}")
    print(f"   • Résumé: {summary_path}")
    print(f"   • Logs: {save_dir}")
    
    # Export ONNX pour edge deployment
    print("\n" + "=" * 70)
    print("📦 Export ONNX pour déploiement edge...")
    print("=" * 70)
    
    try:
        onnx_path = model.export(
            format="onnx",
            imgsz=args.imgsz,
            simplify=True,
            dynamic=False,
            half=False,  # FP32 pour compatibilité
        )
        print(f"✅ Modèle ONNX exporté: {onnx_path}")
        
        # Copier vers models/weights
        onnx_dst = Path("models/weights/best.onnx")
        if Path(onnx_path).exists():
            shutil.copy2(onnx_path, onnx_dst)
            print(f"✅ Copié vers: {onnx_dst}")
            
    except Exception as e:
        print(f"⚠️  Export ONNX échoué: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 Pipeline d'entraînement terminé avec succès!")
    print("=" * 70)
    
    return summary


def main():
    args = parse_args()
    
    # Vérifier que le fichier dataset existe
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ Erreur: Le fichier dataset {args.data} n'existe pas!")
        print("   Lancez d'abord: python scripts/download_fire_dataset.py")
        sys.exit(1)
    
    # Lancer l'entraînement
    train(args)


if __name__ == "__main__":
    main()
