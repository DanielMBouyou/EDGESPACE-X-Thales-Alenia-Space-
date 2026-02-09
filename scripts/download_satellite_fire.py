"""
EDGE SPACE - Téléchargement du dataset satellite wildfire detection
Utilise Roboflow Universe pour télécharger des images satellite annotées de feux.

Datasets disponibles (imagerie satellite):
1. satellite-inferno-dataset (10k images satellite, classe: fire)
2. UMBC Wildfire Detection Satellite (3.8k images, classes: Smoke, Wildfire)

Usage:
    python scripts/download_satellite_fire.py --api-key YOUR_ROBOFLOW_API_KEY

Pour obtenir une clé API gratuite:
1. Créer un compte sur https://app.roboflow.com/
2. Aller dans Settings > API Key
3. Copier la clé
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Download satellite wildfire dataset")
    p.add_argument(
        "--api-key",
        default=os.environ.get("ROBOFLOW_API_KEY", ""),
        help="Roboflow API key (or set ROBOFLOW_API_KEY env var)"
    )
    p.add_argument(
        "--dataset",
        choices=["inferno", "umbc", "both"],
        default="inferno",
        help="Which dataset to download"
    )
    p.add_argument(
        "--output",
        default="datasets/satellite_fire",
        help="Output directory"
    )
    return p.parse_args()


def download_satellite_inferno(api_key: str, output_dir: str):
    """
    Download satellite-inferno-dataset (10k satellite fire images)
    Source: https://universe.roboflow.com/anmatngu-zfleq/satellite-inferno-dataset
    """
    from roboflow import Roboflow

    print("=" * 60)
    print("🛰️  Dataset: satellite-inferno-dataset")
    print("   10,000 images satellite de feux de forêt")
    print("   Classe: fire")
    print("   Licence: CC BY 4.0")
    print("=" * 60)

    rf = Roboflow(api_key=api_key)
    project = rf.workspace("anmatngu-zfleq").project("satellite-inferno-dataset")
    version = project.version(1)
    dataset = version.download("yolov8", location=output_dir)

    print(f"\n✅ Dataset téléchargé dans: {output_dir}")
    return dataset


def download_umbc_wildfire(api_key: str, output_dir: str):
    """
    Download UMBC Wildfire Detection Satellite dataset (3.8k images)
    Source: https://universe.roboflow.com/umbc-s6g8c/wildfire-detection-satellite
    Classes: Smoke, Wildfire
    """
    from roboflow import Roboflow

    print("=" * 60)
    print("🛰️  Dataset: UMBC Wildfire Detection Satellite")
    print("   3,800 images satellite")
    print("   Classes: Smoke, Wildfire")
    print("   Licence: CC BY 4.0")
    print("=" * 60)

    rf = Roboflow(api_key=api_key)
    project = rf.workspace("umbc-s6g8c").project("wildfire-detection-satellite")
    version = project.version(7)
    dataset = version.download("yolov8", location=output_dir)

    print(f"\n✅ Dataset téléchargé dans: {output_dir}")
    return dataset


def create_dataset_yaml(dataset_dir: str, dataset_name: str):
    """Crée/vérifie le fichier data.yaml pour l'entraînement YOLO."""
    dataset_path = Path(dataset_dir)

    # Roboflow crée automatiquement un data.yaml, on le vérifie
    yaml_path = dataset_path / "data.yaml"
    if yaml_path.exists():
        print(f"\n✅ data.yaml trouvé: {yaml_path}")
        print(f"   Contenu:")
        print(yaml_path.read_text(encoding="utf-8"))
    else:
        print(f"\n⚠️  data.yaml non trouvé, création manuelle...")
        # Chercher les dossiers d'images
        train_dir = dataset_path / "train" / "images"
        val_dir = dataset_path / "valid" / "images"
        test_dir = dataset_path / "test" / "images"

        if not train_dir.exists():
            train_dir = dataset_path / "images" / "train"
            val_dir = dataset_path / "images" / "val"
            test_dir = dataset_path / "images" / "test"

        yaml_content = f"""# EDGE SPACE - Satellite Wildfire Detection Dataset
# Source: Roboflow Universe ({dataset_name})

path: {dataset_path.resolve().as_posix()}
train: {train_dir.relative_to(dataset_path).as_posix()}
val: {val_dir.relative_to(dataset_path).as_posix()}
"""
        if test_dir.exists():
            yaml_content += f"test: {test_dir.relative_to(dataset_path).as_posix()}\n"

        if dataset_name == "inferno":
            yaml_content += """
nc: 1
names:
  0: fire
"""
        else:
            yaml_content += """
nc: 2
names:
  0: Smoke
  1: Wildfire
"""
        yaml_path.write_text(yaml_content, encoding="utf-8")
        print(f"✅ data.yaml créé: {yaml_path}")
        print(yaml_content)

    return yaml_path


def count_dataset_stats(dataset_dir: str):
    """Affiche les statistiques du dataset."""
    dataset_path = Path(dataset_dir)

    for split in ["train", "valid", "test"]:
        img_dir = dataset_path / split / "images"
        lbl_dir = dataset_path / split / "labels"
        if not img_dir.exists():
            img_dir = dataset_path / "images" / split
            lbl_dir = dataset_path / "labels" / split

        if img_dir.exists():
            n_images = len(list(img_dir.glob("*")))
            n_labels = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0
            print(f"   {split:6s}: {n_images:5d} images, {n_labels:5d} labels")


def main():
    args = parse_args()

    if not args.api_key:
        print("=" * 60)
        print("❌ Clé API Roboflow requise!")
        print("=" * 60)
        print()
        print("Pour obtenir une clé API GRATUITE:")
        print("  1. Créer un compte: https://app.roboflow.com/")
        print("  2. Settings > Roboflow API > Private API Key")
        print("  3. Relancer:")
        print()
        print('  python scripts/download_satellite_fire.py --api-key "VOTRE_CLE"')
        print()
        print("  Ou définir la variable d'environnement:")
        print('  $env:ROBOFLOW_API_KEY="VOTRE_CLE"')
        print()
        sys.exit(1)

    output_base = Path(args.output)

    print()
    print("🛰️🔥 EDGE SPACE - Téléchargement Dataset Satellite Fire")
    print()

    if args.dataset in ("inferno", "both"):
        inferno_dir = str(output_base / "inferno") if args.dataset == "both" else str(output_base)
        download_satellite_inferno(args.api_key, inferno_dir)
        yaml_path = create_dataset_yaml(inferno_dir, "inferno")
        print("\n📊 Statistiques du dataset:")
        count_dataset_stats(inferno_dir)

    if args.dataset in ("umbc", "both"):
        umbc_dir = str(output_base / "umbc") if args.dataset == "both" else str(output_base)
        download_umbc_wildfire(args.api_key, umbc_dir)
        yaml_path = create_dataset_yaml(umbc_dir, "umbc")
        print("\n📊 Statistiques du dataset:")
        count_dataset_stats(umbc_dir)

    print()
    print("=" * 60)
    print("✅ Téléchargement terminé!")
    print(f"   Dataset: {output_base}")
    print()
    print("   Pour lancer l'entraînement:")
    print(f'   python src/train/train_optimized.py --data "{yaml_path}"')
    print("=" * 60)


if __name__ == "__main__":
    main()
