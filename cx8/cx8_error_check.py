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

ERROR_KEYWORDS = [
    "cx8",
    "connectx-8",
    "mlx5",
    "firmware",
    "link down",
    "bad signal integrity",
    "negotiation failure",
    "timeout",
    "failed",
    "error"
]


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )


def get_cx8_bdfs():
    result = run_command(
        "lspci | grep -i 'Ethernet controller' | grep -i 'ConnectX-8'"
    )

    bdfs = []

    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            bdfs.append(line.split()[0])

    return bdfs


def get_cx8_interfaces():
    interfaces = []

    result = run_command("ls /sys/class/net")

    for iface in result.stdout.split():
        device_path = f"/sys/class/net/{iface}/device"

        if not os.path.exists(device_path):
            continue

        bdf = os.path.basename(os.path.realpath(device_path))

        if bdf in get_cx8_bdfs():
            interfaces.append(iface)

    return sorted(interfaces)


def main():
    print("===== CX8 ERROR CHECK =====\n")

    if not HAS_CX8:
        print("SKIP: This platform does not have CX8")
        return True  

    bdfs = get_cx8_bdfs()
    interfaces = get_cx8_interfaces()

    print(f"Expected CX8 Count : {EXPECTED_CX8_COUNT}")
    print(f"Detected CX8 Count : {len(bdfs)}")
    print(f"CX8 BDFs           : {', '.join(bdfs) if bdfs else 'N/A'}")
    print(f"CX8 Interfaces     : {', '.join(interfaces) if interfaces else 'N/A'}\n")

    if len(bdfs) == 0:
        if EXPECTED_CX8_COUNT == 0:
            print("PASS: No CX8 expected on this platform")
            return True
        else:
            print("FAIL: CX8 expected but no CX8 device detected")
            return False

    result = run_command(
        "dmesg | grep -i -E 'mlx5|connectx|cx8|firmware|link|error|failed|timeout|negotiation'"
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("PASS: No CX8 related error found in dmesg")
        return True

    warning_count = 0

    for line in result.stdout.strip().splitlines():
        lower_line = line.lower()

        related_to_cx8 = (
            any(bdf.lower() in lower_line for bdf in bdfs)
            or any(iface.lower() in lower_line for iface in interfaces)
            or "connectx-8" in lower_line
            or "cx8" in lower_line
        )

        has_error_keyword = any(keyword in lower_line for keyword in ERROR_KEYWORDS)

        if related_to_cx8 and has_error_keyword:
            print(line)
            warning_count += 1

    print("\n==============================")

    if warning_count == 0:
        print("PASS: No CX8 related error found")
        return True
    else:
        print(f"WARNING: Found {warning_count} possible CX8 related log lines")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)