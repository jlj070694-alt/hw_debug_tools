import os
import subprocess
from datetime import datetime

# EXPECTED_DIR = "sensors/expected"
# LOG_DIR = "logs"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPECTED_DIR = os.path.join(
    PROJECT_ROOT,
    "sensors",
    "expected"
)

LOG_DIR = os.path.join(
    PROJECT_ROOT,
    "logs"
)

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def select_platform():
    platforms = {
        "1": "gb300",
        "2": "gb200",
        "3": "h100",
        "4": "b200",
    }

    print("\n===== SELECT PLATFORM =====")
    for key, value in platforms.items():
        print(f"{key}. {value.upper()}")

    choice = input("\nSelect platform: ").strip()

    return platforms.get(choice, "gb300")

def collect_sensor_names():
    result = run_command("ipmitool sdr elist")

    if result.returncode != 0:
        print("FAIL: Unable to execute ipmitool")
        print(result.stderr)
        return []

    sensors = []

    for line in result.stdout.splitlines():
        if "|" in line:
            sensor_name = line.split("|")[0].strip()

            if sensor_name:
                sensors.append(sensor_name)

    return sensors, result.stdout

def write_expected_file(platform, sensors):
    os.makedirs(EXPECTED_DIR, exist_ok=True)

    file_path = os.path.join(
        EXPECTED_DIR,
        f"{platform}_expected_sensors.txt"
    )

    with open(file_path, "w") as f:
        for sensor in sensors:
            f.write(sensor + "\n")

    return file_path

def write_raw_log(platform, raw_output):
    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = os.path.join(
        LOG_DIR,
        f"{platform}_golden_sensor_raw_{timestamp}.txt"
    )

    with open(log_file, "w") as f:
        f.write(raw_output)

    return log_file

def main():
    print("===== GOLDEN SENSOR COLLECTOR =====")
    print("Run this script only on a known-good node.\n")

    platform = select_platform()

    result = collect_sensor_names()

    if not result:
        return

    sensors, raw_output = result

    if not sensors:
        print("FAIL: No sensors collected")
        return

    print(f"\nPlatform: {platform.upper()}")
    print(f"Collected Sensor Count: {len(sensors)}")

    print("\n===== SENSOR PREVIEW =====")
    for sensor in sensors[:10]:
        print(sensor)

    if len(sensors) > 10:
        print(f"... {len(sensors) - 10} more sensors")

    confirm = input("\nGenerate golden sensor file? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Canceled.")
        return

    expected_file = write_expected_file(platform, sensors)
    raw_log = write_raw_log(platform, raw_output)

    print("\nPASS: Golden sensor data collected")
    print(f"Expected sensor file: {expected_file}")
    print(f"Raw sensor log      : {raw_log}")

if __name__ == "__main__":
    main()