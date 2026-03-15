import argparse
import json
from pathlib import Path
from typing import Any

import cv2
from ultralytics import YOLO


DEFAULT_BALL_CLASSES = ["sports ball", "frisbee", "orange", "apple", "baseball"]

_REPO_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _REPO_ROOT / "output"
_IMAGES_DIR = _OUTPUT_DIR / "images"
_ANALYSIS_DIR = _OUTPUT_DIR / "analysis"
_ANNOTATED_DIR = _ANALYSIS_DIR / "annotated"


def list_image_files(input_dir: Path) -> list[Path]:
    extensions = ("*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG")
    files: list[Path] = []
    for pattern in extensions:
        files.extend(input_dir.glob(pattern))
    return sorted({p.resolve() for p in files})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect person/head proxy and ball from image(s) using YOLO.")
    parser.add_argument("--image", default=None, help="Optional single image path")
    parser.add_argument("--input-dir", default=str(_IMAGES_DIR), help="Input directory for batch mode")
    parser.add_argument("--model", default="yolov8l.pt", help="YOLO model file or model name")
    parser.add_argument(
        "--ball-classes",
        default=",".join(DEFAULT_BALL_CLASSES),
        help="Comma-separated YOLO classes to treat as ball",
    )
    parser.add_argument("--conf-person", type=float, default=0.35, help="Confidence threshold for person (default: 0.35)")
    parser.add_argument("--conf-ball", type=float, default=0.03, help="Confidence threshold for ball (default: 0.03)")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold (default: 0.45)")
    parser.add_argument("--save-annotated", default=None, help="Annotated output image path for single-image mode")
    parser.add_argument("--annotated-dir", default=str(_ANNOTATED_DIR), help="Annotated output directory for batch mode")
    parser.add_argument("--save-json", default=str(_ANALYSIS_DIR / "detections_all.json"), help="Detection output JSON")
    parser.add_argument("--debug", action="store_true", help="Print all raw YOLO detections before filtering")
    return parser.parse_args()


def parse_csv_labels(labels: str) -> set[str]:
    return {item.strip().lower() for item in labels.split(",") if item.strip()}


def person_head_box(person_box: list[float]) -> list[float]:
    x1, y1, x2, y2 = person_box
    height = y2 - y1
    head_y2 = y1 + (0.35 * height)
    return [x1, y1, x2, head_y2]


def to_int_box(box: list[float]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return int(x1), int(y1), int(x2), int(y2)


def draw_box(image, box: list[float], label: str, color: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = to_int_box(box)
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    cv2.putText(image, label, (x1, max(y1 - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)


def analyze_image(result: Any, image_path: Path, args: argparse.Namespace, annotated_path: Path) -> dict[str, Any] | None:
    source_img = cv2.imread(str(image_path))
    if source_img is None:
        print(f"Failed to read image: {image_path}")
        return None

    if args.debug:
        print(f"--- raw detections for {image_path.name} ---")
        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = result.names[cls_id]
            conf = float(box.conf[0])
            print(f"  {cls_name:20s} conf={conf:.4f}")
        print("---")

    detections: list[dict[str, Any]] = []
    counts = {"person": 0, "ball": 0, "head_estimate": 0}
    target_classes = {"person", *args.ball_class_set}

    for box in result.boxes:
        cls_id = int(box.cls[0])
        cls_name = result.names[cls_id].lower()
        if cls_name not in target_classes:
            continue

        conf = float(box.conf[0])
        xyxy = [float(v) for v in box.xyxy[0].tolist()]

        if cls_name == "person" and conf < args.conf_person:
            continue
        if cls_name in args.ball_class_set and conf < args.conf_ball:
            continue

        if cls_name == "person":
            label = "person"
            color = (255, 80, 80)
            counts["person"] += 1
        else:
            label = "ball"
            color = (80, 220, 80)
            counts["ball"] += 1

        detections.append(
            {
                "label": label,
                "confidence": round(conf, 4),
                "bbox_xyxy": [round(v, 2) for v in xyxy],
            }
        )
        draw_box(source_img, xyxy, f"{label} {conf:.2f}", color)

        # Head is estimated as upper 35% of each person bounding box.
        if label == "person":
            head_box = person_head_box(xyxy)
            counts["head_estimate"] += 1
            detections.append(
                {
                    "label": "head_estimate",
                    "confidence": round(conf, 4),
                    "bbox_xyxy": [round(v, 2) for v in head_box],
                    "source": "person_bbox_top_region",
                }
            )
            draw_box(source_img, head_box, "head_estimate", (80, 180, 255))

    annotated_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(annotated_path), source_img)

    return {
        "image": str(image_path),
        "counts": counts,
        "detections": detections,
        "annotated_image": str(annotated_path),
    }


def main() -> int:
    args = parse_args()
    args.ball_class_set = parse_csv_labels(args.ball_classes)

    if args.image:
        image_paths = [Path(args.image).resolve()]
        mode = "single"
    else:
        input_dir = Path(args.input_dir).resolve()
        if not input_dir.exists():
            print(f"Input directory not found: {input_dir}")
            return 1
        image_paths = list_image_files(input_dir)
        mode = "directory"

    if not image_paths:
        print("No .png/.jpg/.jpeg files found to analyze")
        return 1

    model = YOLO(args.model)
    min_conf = min(args.conf_person, args.conf_ball)

    json_path = Path(args.save_json).resolve()
    annotated_dir = Path(args.annotated_dir).resolve()

    all_results: list[dict[str, Any]] = []
    summary = {
        "images_total": len(image_paths),
        "images_processed": 0,
        "person": 0,
        "head_estimate": 0,
        "ball": 0,
        "images_with_ball": 0,
    }

    for image_path in image_paths:
        if not image_path.exists():
            print(f"Input image not found: {image_path}")
            continue

        results = model.predict(source=str(image_path), conf=min_conf, iou=args.iou, verbose=False, device="cpu")
        result = results[0]

        if mode == "single" and args.save_annotated:
            annotated_path = Path(args.save_annotated).resolve()
        else:
            annotated_path = annotated_dir / f"{image_path.stem}_annotated{image_path.suffix}"

        item = analyze_image(result=result, image_path=image_path, args=args, annotated_path=annotated_path)
        if item is None:
            continue

        all_results.append(item)
        summary["images_processed"] += 1
        summary["person"] += item["counts"]["person"]
        summary["head_estimate"] += item["counts"]["head_estimate"]
        summary["ball"] += item["counts"]["ball"]
        if item["counts"]["ball"] > 0:
            summary["images_with_ball"] += 1

        print(
            f"{image_path.name}: person={item['counts']['person']}, "
            f"head_estimate={item['counts']['head_estimate']}, ball={item['counts']['ball']}"
        )

    if summary["images_processed"] == 0:
        print("No images were processed successfully")
        return 1

    payload = {
        "mode": mode,
        "model": args.model,
        "summary": summary,
        "results": all_results,
    }

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2))

    print(f"Detection report saved to: {json_path}")
    print(
        "Summary: "
        f"images={summary['images_processed']}/{summary['images_total']}, "
        f"person={summary['person']}, head_estimate={summary['head_estimate']}, "
        f"ball={summary['ball']}, images_with_ball={summary['images_with_ball']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())