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
            or "bf3" in text
            or "connectx-7" in text
        )
    )


def get_bf3_interfaces():
    result = run_command("ls /sys/class/net")

    interfaces = []

    for iface in result.stdout.split():
        if is_bf3_interface(iface):
            interfaces.append(iface)

    return sorted(interfaces)


def get_operstate(iface):
    result = run_command(f"cat /sys/class/net/{iface}/operstate")
    return result.stdout.strip()


def get_ip_address(iface):
    result = run_command(
        f"ip -4 addr show {iface} | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){{3}}'"
    )
    return result.stdout.strip()


def main():
    print("===== BF3 NETWORK CHECK =====\n")

    if not HAS_BF3:
        print("SKIP: This platform does not have BF3")
        return True

    interfaces = get_bf3_interfaces()
    detected_count = len(interfaces)

    print(f"Expected BF3 Count : {EXPECTED_BF3_COUNT}")
    print(f"Detected BF3 Count : {detected_count}\n")

    if detected_count == 0:
        print(
            f"FAIL: Expected {EXPECTED_BF3_COUNT} BF3 interface(s), "
            "but detected 0"
        )
        return False

    overall_pass = True

    if detected_count != EXPECTED_BF3_COUNT:
        print(
            f"WARNING: Expected {EXPECTED_BF3_COUNT} BF3 interface(s), "
            f"but detected {detected_count}"
        )
        print("Continue checking detected BF3 network interfaces...\n")
        overall_pass = False

    print(f"{'Interface':<12} {'BDF':<15} {'State':<10} {'IPv4 Address'}")
    print("-" * 60)

    for iface in interfaces:
        bdf = get_interface_bdf(iface)
        state = get_operstate(iface)
        ip_addr = get_ip_address(iface)

        if not ip_addr:
            ip_addr = "N/A"

        print(f"{iface:<12} {bdf:<15} {state:<10} {ip_addr}")

        if state != "up":
            overall_pass = False

    print("\n===== ETHTOOL SUMMARY =====")

    for iface in interfaces:
        print(f"\nInterface: {iface}")
        print(f"BDF      : {get_interface_bdf(iface)}")

        result = run_command(f"ethtool {iface}")

        if result.returncode != 0:
            print("FAIL: ethtool failed")
            print(result.stderr)
            overall_pass = False
            continue

        for line in result.stdout.splitlines():
            if (
                "Speed:" in line
                or "Duplex:" in line
                or "Link detected:" in line
                or "Auto-negotiation:" in line
            ):
                print(line)

    print("\n==============================")

    if overall_pass:
        print("PASS: BF3 network check passed")
        return True
    else:
        print("FAIL: One or more BF3 network interfaces have issue")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)