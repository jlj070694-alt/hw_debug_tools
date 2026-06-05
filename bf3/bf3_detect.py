import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

HAS_BF3 = getattr(cfg, "HAS_BF3", False)
EXPECTED_BF3_COUNT = cfg.EXPECTED_BF3_COUNT


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )


def main():

    print("===== BF3 DETECTION CHECK =====\n")

    if not HAS_BF3:
        print("SKIP: This platform does not have BF3")
        return True
    
    result = run_command(
        "lspci | grep -i -E 'BlueField|BF3|DPU'"
    )

    bf3_lines = []

    if result.returncode == 0 and result.stdout.strip():
        bf3_lines = result.stdout.strip().splitlines()

    bf3_count = len(bf3_lines)

    print(f"Expected BF3 count: {EXPECTED_BF3_COUNT}")
    print(f"Detected BF3 count: {bf3_count}")

    if bf3_count == EXPECTED_BF3_COUNT:

        print("PASS: BF3 count is correct")

    else:

        print(
            f"FAIL: Expected {EXPECTED_BF3_COUNT}, "
            f"but detected {bf3_count}"
        )

    print("\n===== BF3 LIST =====")

    if bf3_lines:

        for bf3 in bf3_lines:
            print(bf3)

    else:

        print("No BF3 detected")


if __name__ == "__main__":
    main()