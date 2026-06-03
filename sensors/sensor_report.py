# import subprocess
# import os
# from datetime import datetime

import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.gb300_config import EXPECTED_SENSOR_COUNT

REPORT_DIR = "logs"

# EXPECTED_SENSOR_COUNT = 116

def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout

def main():

    os.makedirs(REPORT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_file = (
        f"{REPORT_DIR}/sensor_report_{timestamp}.txt"
    )

    print("Generating Sensor Report...")

    sensor_output = run_command(
        "ipmitool sdr elist"
    )

    sensor_lines = []

    for line in sensor_output.splitlines():
        if "|" in line:
            sensor_lines.append(line)

    sensor_count = len(sensor_lines)

    unhealthy_sensors = []

    bad_keywords = [
        "cr",
        "nc",
        "nr",
        "not present",
        "unavailable",
        "failed"
    ]

    for line in sensor_lines:

        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in bad_keywords
        ):
            unhealthy_sensors.append(line)

    with open(report_file, "w") as f:

        f.write(
            "========== SENSOR REPORT ==========\n"
        )

        f.write(
            f"Generated Time : {timestamp}\n\n"
        )

        f.write(
            f"Expected Sensor Count : "
            f"{EXPECTED_SENSOR_COUNT}\n"
        )

        f.write(
            f"Detected Sensor Count : "
            f"{sensor_count}\n\n"
        )

        if sensor_count == EXPECTED_SENSOR_COUNT:
            f.write(
                "Sensor Count Result : PASS\n\n"
            )
        else:
            f.write(
                "Sensor Count Result : FAIL\n\n"
            )

        f.write(
            "===== Unhealthy Sensors =====\n"
        )

        if unhealthy_sensors:

            for sensor in unhealthy_sensors:
                f.write(sensor + "\n")

        else:
            f.write(
                "No unhealthy sensors found.\n"
            )

        f.write(
            "\n===== Full Sensor List =====\n"
        )

        for sensor in sensor_lines:
            f.write(sensor + "\n")

    print(
        f"PASS: Report generated:\n{report_file}"
    )

if __name__ == "__main__":
    main()