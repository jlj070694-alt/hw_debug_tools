import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

EXPECTED_E1S_COUNT = cfg.EXPECTED_E1S_COUNT


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )


def main():

    print("===== E1.S DETECTION CHECK =====\n")

    result = run_command("nvme list")

    e1s_lines = []

    if result.returncode == 0 and result.stdout.strip():

        for line in result.stdout.splitlines():

            if "/dev/nvme" in line:
                e1s_lines.append(line)

    e1s_count = len(e1s_lines)

    print(f"Expected E1.S count: {EXPECTED_E1S_COUNT}")
    print(f"Detected E1.S count: {e1s_count}")

    if e1s_count == EXPECTED_E1S_COUNT:

        print("PASS: E1.S count is correct")

    else:

        print(
            f"FAIL: Expected {EXPECTED_E1S_COUNT}, "
            f"but detected {e1s_count}"
        )

    print("\n===== E1.S LIST =====")

    if e1s_lines:

        for drive in e1s_lines:
            print(drive)

    else:

        print("No E1.S detected")


if __name__ == "__main__":
    main()