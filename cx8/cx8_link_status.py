import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

EXPECTED_CX8_COUNT = cfg.EXPECTED_CX8_COUNT
REQUIRE_CX8_LINK_UP = getattr(cfg, "REQUIRE_CX8_LINK_UP", True)


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


def check_link_status(iface):
    result = run_command(f"cat /sys/class/net/{iface}/operstate")
    return result.stdout.strip()


def main():
    print("===== CX8 LINK STATUS CHECK =====\n")

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
            f"FAIL: Expected {EXPECTED_CX8_COUNT} CX8 interface(s), "
            f"but detected {detected_count}"
        )
        overall_pass = False

    print("===== CX8 LINK STATUS =====")

    for iface in interfaces:
        status = check_link_status(iface)
        bdf = get_interface_bdf(iface)

        print(f"{iface:<12} BDF: {bdf:<15} State: {status}")

        if REQUIRE_CX8_LINK_UP and status != "up":
            print(f"FAIL: {iface} link is not up")
            overall_pass = False
        elif not REQUIRE_CX8_LINK_UP and status != "up":
            print(f"WARNING: {iface} link is not up")

    print("\n==============================")

    if overall_pass:
        print("PASS: CX8 link status check passed")
        return True
    else:
        print("FAIL: CX8 link status check failed")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)