import subprocess
import os

EXPECTED_FILE = "sensors/expected_sensors.txt"

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def load_expected_sensors():
    if not os.path.exists(EXPECTED_FILE):
        print(f"FAIL: Expected sensor file not found: {EXPECTED_FILE}")
        return []

    with open(EXPECTED_FILE, "r") as f:
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