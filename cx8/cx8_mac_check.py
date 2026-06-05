import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

HAS_CX8 = getattr(cfg, "HAS_CX8", False)
EXPECTED_CX8_COUNT = cfg.EXPECTED_CX8_COUNT

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_cx8_interfaces():

    interfaces = []

    result = run_command("ls /sys/class/net")

    for iface in result.stdout.split():

        device_path = f"/sys/class/net/{iface}/device"

        if os.path.exists(device_path):

            vendor = run_command(
                f"cat {device_path}/vendor"
            ).stdout.strip()

            if vendor == "0x15b3":
                interfaces.append(iface)

    return sorted(interfaces)

def get_mac_address(iface):

    result = run_command(
        f"cat /sys/class/net/{iface}/address"
    )

    return result.stdout.strip()

def main():

    print("===== CX8 MAC ADDRESS CHECK =====\n")

    if not HAS_CX8:
        print("SKIP: This platform does not have CX8")
        return True  

    interfaces = get_cx8_interfaces()

    if not interfaces:
        print("FAIL: No CX8 interfaces found")
        return

    print(f"{'Interface':<15} {'MAC Address'}")
    print("-" * 40)

    for iface in interfaces:

        mac = get_mac_address(iface)

        print(f"{iface:<15} {mac}")

    print("\nPASS: MAC collection completed")

if __name__ == "__main__":
    main()