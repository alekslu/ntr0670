import argparse
import os
import sys
import time

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture one frame from USB camera on Windows.")
    parser.add_argument("--cam-index", type=int, default=0, help="OpenCV camera index (default: 0)")
    parser.add_argument(
        "--output",
        required=True,
        help="Output image path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(args.cam_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Failed to open USB camera at index {args.cam_index}")
        return 1

    # Warm up camera and discard initial unstable frames.
    time.sleep(1.0)
    for _ in range(5):
        cap.read()

    ret, frame = cap.read()
    if ret and frame is not None:
        cv2.imwrite(args.output, frame)
        print(f"Saved image to {args.output}")
        cap.release()
        return 0

    print("Failed to capture image")
    cap.release()
    return 1


if __name__ == "__main__":
    sys.exit(main())
