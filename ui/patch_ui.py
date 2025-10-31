import fileinput
from pathlib import Path
import sys
import signal


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if len(sys.argv) != 2:
        print("Usage: python patch_ui.py <path_to_ui_python_file>")
        sys.exit(1)

    ui_path: Path = Path(sys.argv[1]).resolve()
    if not ui_path.exists():
        print(f"❌ File not found: {ui_path}")
        sys.exit(1)


    replacements: tuple[tuple[str, str]] = (
        ("../icons/", "./ui/icons/"),
    )

    for line in fileinput.input(ui_path, inplace=True, encoding="utf-8"):
        # print(line)
        for s, r in replacements:
            # print(f"{s} -> {r}")
            if s in line:
                line = line.replace(s, r)
                break
        sys.stdout.write(line)


    print("✅ Patched \'icons\' directory")
