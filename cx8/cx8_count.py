# import subprocess

# EXPECTED_CX8_COUNT = 8

import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

EXPECTED_CX8_COUNT = cfg.EXPECTED_CX8_COUNT

# from config.gb300_config import EXPECTED_CX8_COUNT

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def main():
    print("===== CX8 COUNT CHECK =====")

    result = run_command("lspci | grep -i 'Ethernet controller' | grep -i 'ConnectX-8'")

    if result.returncode != 0 or not result.stdout.strip():
        print("FAIL: No CX8 / Mellanox NIC detected")
        print(result.stderr)
        return

    cx8_lines = result.stdout.strip().splitlines()
    cx8_count = len(cx8_lines)

    print(f"Detected CX8 count: {cx8_count}")

    if cx8_count == EXPECTED_CX8_COUNT:
        print("PASS: CX8 count is correct")
    else:
        print(f"FAIL: Expected {EXPECTED_CX8_COUNT}, but detected {cx8_count}")

    print("\n===== CX8 LIST =====")
    for cx8 in cx8_lines:
        print(cx8)

if __name__ == "__main__":
    main()