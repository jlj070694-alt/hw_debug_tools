import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

HAS_BF3 = getattr(cfg, "HAS_BF3", False)
EXPECTED_BF3_COUNT = getattr(cfg, "EXPECTED_BF3_COUNT", 0)
EXPECTED_BF3_FW = getattr(cfg, "EXPECTED_BF3_FW", "N/A")


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


def is_bf3_interface(iface):
    bdf = get_interface_bdf(iface)

    if not bdf:
        return False

    result = run_command(f"lspci -s {bdf}")
    text = result.stdout.lower()

    return (
        "ethernet controller" in text
        and (
            "bluefield" in text
            or "connectx-7" in text
            or "bf3" in text
        )
    )


def get_bf3_interfaces():
    result = run_command("ls /sys/class/net")

    interfaces = []

    for iface in result.stdout.split():
        if is_bf3_interface(iface):
            interfaces.append(iface)

    return sorted(interfaces)


def main():
    print("===== BF3 FW CHECK =====\n")

    if not HAS_BF3:
        print("SKIP: This platform does not have BF3")
        return True

    interfaces = get_bf3_interfaces()
    detected_count = len(interfaces)

    print(f"Expected BF3 Count : {EXPECTED_BF3_COUNT}")
    print(f"Detected BF3 Count : {detected_count}")
    print(f"Expected BF3 FW    : {EXPECTED_BF3_FW}\n")

    if detected_count == 0:
        print(
            f"FAIL: Expected {EXPECTED_BF3_COUNT} BF3 interface(s), "
            f"but detected 0"
        )
        return False

    overall_pass = True

    if detected_count != EXPECTED_BF3_COUNT:
        print(
            f"WARNING: Expected {EXPECTED_BF3_COUNT} BF3 interface(s), "
            f"but detected {detected_count}"
        )
        print("Continue checking detected BF3 firmware...\n")
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

        fw_version = "Unknown"

        for line in result.stdout.splitlines():
            if (
                "driver:" in line
                or "version:" in line
                or "firmware-version:" in line
                or "bus-info:" in line
            ):
                print(line)

            if "firmware-version:" in line:
                fw_version = line.split(":", 1)[1].strip()

        if EXPECTED_BF3_FW == "N/A":
            print("WARNING: Expected BF3 firmware is not defined in config\n")
            overall_pass = False
        elif EXPECTED_BF3_FW in fw_version:
            print("FW Check : PASS\n")
        else:
            print("FW Check : FAIL")
            print(f"Expected : {EXPECTED_BF3_FW}")
            print(f"Actual   : {fw_version}\n")
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: BF3 firmware check passed")
        return True
    else:
        print("FAIL: BF3 firmware check completed with issue")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)