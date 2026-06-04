# import subprocess
# from config.gb300_config import EXPECTED_GPU_COUNT
import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

EXPECTED_GPU_COUNT = cfg.EXPECTED_GPU_COUNT


# from config.gb300_config import EXPECTED_GPU_COUNT


def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result

def main():
    print("===== GPU COUNT CHECK =====")

    result = run_command("nvidia-smi -L")

    # if result.returncode != 0:
    #     print("FAIL: Cannot run nvidia-smi")
    #     print(result.stderr)
    #     return

    # gpu_lines = result.stdout.strip().splitlines()
    # gpu_count = len(gpu_lines)

    gpu_lines = []

    if result.returncode == 0 and result.stdout.strip():
        gpu_lines = [
            line for line in result.stdout.strip().splitlines()
            if line.startswith("GPU ")
        ]

    gpu_count = len(gpu_lines)

    print(f"Expected GPU count: {EXPECTED_GPU_COUNT}")
    print(f"Detected GPU count: {gpu_count}")

    if gpu_count == EXPECTED_GPU_COUNT:
        print("PASS: GPU count is correct")
    else:
        print(f"FAIL: Expected {EXPECTED_GPU_COUNT}, but detected {gpu_count}")

        if result.stderr.strip():
            print("\n===== ERROR =====")
            print(result.stderr.strip())

    print("\n===== GPU LIST =====")

    if gpu_lines:
        for gpu in gpu_lines:
            print(gpu)
    else:
        print("No GPU detected by nvidia-smi")
        
if __name__ == "__main__":
    main()