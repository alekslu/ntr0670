import subprocess
from pathlib import Path


def wsl_to_windows_path(path: Path) -> str:
    result = subprocess.run(
        ["wslpath", "-w", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    win_script_wsl = repo_root / "windows_scripts" / "camera_win.py"
    output_dir_wsl = repo_root / "output"
    output_file_wsl = output_dir_wsl / "webcam.png"

    output_dir_wsl.mkdir(parents=True, exist_ok=True)

    win_script = wsl_to_windows_path(win_script_wsl)
    output_file = wsl_to_windows_path(output_file_wsl)

    cmd = [
        "python.exe",
        win_script,
        "--output",
        output_file,
    ]

    completed = subprocess.run(cmd)
    if completed.returncode == 0:
        print("Image saved:", output_file_wsl)
    else:
        print("Capture failed with code", completed.returncode)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
