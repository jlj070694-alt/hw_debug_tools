# import subprocess

# EXPECTED_DRIVE_COUNT = 8

import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.gb300_config import EXPECTED_E1S_COUNT

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

    if result.returncode != 0:
        print("FAIL: nvme command failed")
        print(result.stderr)
        return

    drives = []

    for line in result.stdout.splitlines():

        if "/dev/nvme" in line:
            drives.append(line)

    detected_count = len(drives)

    print(f"Expected Drive Count : {EXPECTED_E1S_COUNT}")
    print(f"Detected Drive Count : {detected_count}")

    print("\n===== DETECTED DRIVES =====")

    for drive in drives:
        print(drive)

    print("\n============================")

    if detected_count == EXPECTED_E1S_COUNT:
        print("PASS: All E1.S drives detected")
    else:
        missing = EXPECTED_E1S_COUNT - detected_count

        print(
            f"FAIL: Missing {missing} drive(s)"
        )

if __name__ == "__main__":
    main()