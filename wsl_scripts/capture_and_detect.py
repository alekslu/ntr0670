import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture image from camera, then run YOLO detection.")
    parser.add_argument("--model", default="yolov8l.pt", help="YOLO model name/path")
    parser.add_argument("--conf-person", type=float, default=0.35, help="Confidence threshold for person")
    parser.add_argument("--conf-ball", type=float, default=0.03, help="Confidence threshold for ball")
    return parser.parse_args()


def latest_image(images_dir: Path) -> Path | None:
    candidates = []
    for pattern in ("*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"):
        candidates.extend(images_dir.glob(pattern))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_root = repo_root / "output"

    capture_script = repo_root / "wsl_scripts" / "capture_wsl.py"
    detect_script = repo_root / "wsl_scripts" / "detect_yolo.py"
    images_dir = output_root / "images"
    analysis_dir = output_root / "analysis"

    capture = subprocess.run([sys.executable, str(capture_script)])
    if capture.returncode != 0:
        print("Capture step failed.")
        return capture.returncode

    image_path = latest_image(images_dir)
    if image_path is None:
        print("No image found in output/images after capture")
        return 1

    analysis_dir.mkdir(parents=True, exist_ok=True)
    annotated_path = analysis_dir / "annotated" / f"{image_path.stem}_annotated{image_path.suffix}"
    json_path = analysis_dir / f"{image_path.stem}_detection.json"

    detect = subprocess.run(
        [
            sys.executable,
            str(detect_script),
            "--image",
            str(image_path),
            "--model",
            args.model,
            "--conf-person",
            str(args.conf_person),
            "--conf-ball",
            str(args.conf_ball),
            "--save-annotated",
            str(annotated_path),
            "--save-json",
            str(json_path),
        ]
    )
    if detect.returncode != 0:
        print("Detection step failed.")
    return detect.returncode


if __name__ == "__main__":
    raise SystemExit(main())