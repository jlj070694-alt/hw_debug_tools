import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config, get_platform

cfg = load_config()

SENSOR_EXPECTED_FILE = getattr(
    cfg,
    "EXPECTED_SENSOR_FILE",
    f"sensors/expected/{get_platform().lower()}_expected_sensors.txt"
)

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_expected_file_path():
    if os.path.isabs(SENSOR_EXPECTED_FILE):
        return SENSOR_EXPECTED_FILE

    return os.path.join(PROJECT_ROOT, SENSOR_EXPECTED_FILE)

def load_expected_sensors():
    expected_file = get_expected_file_path()

    if not os.path.exists(expected_file):
        print(f"FAIL: Expected sensor file not found: {expected_file}")
        return []

    with open(expected_file, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_current_sensors():
    result = run_command("ipmitool sdr elist")

    if result.returncode != 0:
        print("FAIL: Unable to execute ipmitool")
        print(result.stderr)
        return []

    sensors = []

    for line in result.stdout.splitlines():
        if "|" in line:
            sensor_name = line.split("|")[0].strip()
            sensors.append(sensor_name)

    return sensors

def main():
    print("===== SENSOR MISSING CHECK =====\n")
    print(f"Platform             : {get_platform()}")
    print(f"Expected Sensor File : {get_expected_file_path()}\n")

    expected = load_expected_sensors()
    current = get_current_sensors()

    if not expected or not current:
        return

    missing = sorted(set(expected) - set(current))
    extra = sorted(set(current) - set(expected))

    print(f"Expected Sensor Count : {len(expected)}")
    print(f"Current Sensor Count  : {len(current)}")

    if missing:
        print("\n===== MISSING SENSORS =====")
        for sensor in missing:
            print(sensor)
    else:
        print("\nPASS: No missing sensors")

    if extra:
        print("\n===== EXTRA SENSORS =====")
        for sensor in extra:
            print(sensor)

    print("\n==============================")

    if missing:
        print(f"FAIL: Missing {len(missing)} sensor(s)")
    else:
        print("PASS: Sensor missing check passed")

if __name__ == "__main__":
    main()