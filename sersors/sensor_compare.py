import sys

def load_sensors(file_path):
    sensors = []

    with open(file_path, "r") as f:
        for line in f:
            if "|" in line:
                sensor_name = line.split("|")[0].strip()

                if sensor_name:
                    sensors.append(sensor_name)

    return set(sensors)

def main():
    print("===== SENSOR COMPARE CHECK =====\n")

    if len(sys.argv) != 3:
        print("Usage:")
        print("python3 sensors/sensor_compare.py good_sensor.txt bad_sensor.txt")
        return

    good_file = sys.argv[1]
    bad_file = sys.argv[2]

    good_sensors = load_sensors(good_file)
    bad_sensors = load_sensors(bad_file)

    missing = sorted(good_sensors - bad_sensors)
    extra = sorted(bad_sensors - good_sensors)

    print(f"Good Node Sensor Count : {len(good_sensors)}")
    print(f"Bad Node Sensor Count  : {len(bad_sensors)}")

    if missing:
        print("\n===== MISSING IN BAD NODE =====")
        for sensor in missing:
            print(sensor)
    else:
        print("\nPASS: No missing sensors in bad node")

    if extra:
        print("\n===== EXTRA IN BAD NODE =====")
        for sensor in extra:
            print(sensor)

    print("\n==============================")

    if missing:
        print(f"FAIL: Bad node is missing {len(missing)} sensor(s)")
    else:
        print("PASS: Sensor compare passed")

if __name__ == "__main__":
    main()