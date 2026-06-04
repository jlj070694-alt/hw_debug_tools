import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

EXPECTED_SENSOR_COUNT = cfg.EXPECTED_SENSOR_COUNT


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )


def main():

    print("===== SENSOR COUNT CHECK =====\n")

    result = run_command("ipmitool sdr elist")

    sensor_lines = []

    if result.returncode == 0 and result.stdout.strip():

        for line in result.stdout.splitlines():

            if "|" in line:
                sensor_lines.append(line)

    sensor_count = len(sensor_lines)

    print(f"Expected Sensor Count : {EXPECTED_SENSOR_COUNT}")
    print(f"Detected Sensor Count : {sensor_count}")

    print("\n==============================")

    if sensor_count == EXPECTED_SENSOR_COUNT:

        print("PASS: Sensor count is correct")

    else:

        print(
            f"FAIL: Expected {EXPECTED_SENSOR_COUNT}, "
            f"but detected {sensor_count}"
        )

        if result.stderr.strip():
            print("\n===== ERROR =====")
            print(result.stderr.strip())


if __name__ == "__main__":
    main()