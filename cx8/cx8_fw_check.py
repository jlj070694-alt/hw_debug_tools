import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

EXPECTED_CX8_COUNT = cfg.EXPECTED_CX8_COUNT


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )


def get_interface_bdf(iface):
    device_path = f"/sys/class/net/{iface}/device"

    if not os.path.exists(device_path):
        return None

    real_path = os.path.realpath(device_path)
    return os.path.basename(real_path)


def is_cx8_interface(iface):
    bdf = get_interface_bdf(iface)

    if not bdf:
        return False

    result = run_command(f"lspci -s {bdf}")
    text = result.stdout.lower()

    return (
        "ethernet controller" in text
        and "connectx-8" in text
    )


def get_cx8_interfaces():
    result = run_command("ls /sys/class/net")

    interfaces = []

    for iface in result.stdout.split():
        if is_cx8_interface(iface):
            interfaces.append(iface)

    return sorted(interfaces)


def main():
    print("===== CX8 FIRMWARE CHECK =====\n")

    interfaces = get_cx8_interfaces()
    detected_count = len(interfaces)

    print(f"Expected CX8 Count : {EXPECTED_CX8_COUNT}")
    print(f"Detected CX8 Count : {detected_count}\n")

    if detected_count == 0:
        if EXPECTED_CX8_COUNT == 0:
            print("PASS: No CX8 expected on this platform")
            return True
        else:
            print(
                f"FAIL: Expected {EXPECTED_CX8_COUNT} CX8 interface(s), "
                f"but detected 0"
            )
            return False

    overall_pass = True

    if detected_count != EXPECTED_CX8_COUNT:
        print(
            f"WARNING: Expected {EXPECTED_CX8_COUNT} CX8 interface(s), "
            f"but detected {detected_count}"
        )
        print("Continue checking detected CX8 firmware...\n")
        overall_pass = False

    for iface in interfaces:
        bdf = get_interface_bdf(iface)

        print(f"\nInterface: {iface}")
        print(f"BDF      : {bdf}")

        result = run_command(f"ethtool -i {iface}")

        if result.returncode != 0:
            print("FAIL: Cannot get firmware info")
            print(result.stderr)
            overall_pass = False
            continue

        for line in result.stdout.splitlines():
            if (
                "driver:" in line
                or "version:" in line
                or "firmware-version:" in line
                or "bus-info:" in line
            ):
                print(line)

    print("\n==============================")

    if overall_pass:
        print("PASS: CX8 firmware check completed")
        return True
    else:
        print("FAIL: CX8 firmware check completed with issue")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)