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

ERROR_KEYWORDS = [
    "bluefield",
    "bf3",
    "dpu",
    "firmware",
    "pcie",
    "aer",
    "link down",
    "timeout",
    "failed",
    "failure",
    "error",
    "reset",
]


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )


def get_bf3_bdfs():
    result = run_command(
        "lspci | grep -i -E 'BlueField|BlueField-3|BF3|DPU|ConnectX-7'"
    )

    bdfs = []

    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            bdfs.append(line.split()[0])

    return bdfs


def get_interface_bdf(iface):
    device_path = f"/sys/class/net/{iface}/device"

    if not os.path.exists(device_path):
        return None

    real_path = os.path.realpath(device_path)
    return os.path.basename(real_path)


def get_bf3_interfaces():
    bdfs = get_bf3_bdfs()
    interfaces = []

    result = run_command("ls /sys/class/net")

    for iface in result.stdout.split():
        bdf = get_interface_bdf(iface)

        if bdf in bdfs:
            interfaces.append(iface)

    return sorted(interfaces)


def main():
    print("===== BF3 ERROR CHECK =====\n")

    if not HAS_BF3:
        print("SKIP: This platform does not have BF3")
        return True

    bdfs = get_bf3_bdfs()
    interfaces = get_bf3_interfaces()

    print(f"Expected BF3 Count : {EXPECTED_BF3_COUNT}")
    print(f"Detected BF3 Count : {len(bdfs)}")
    print(f"BF3 BDFs           : {', '.join(bdfs) if bdfs else 'N/A'}")
    print(f"BF3 Interfaces     : {', '.join(interfaces) if interfaces else 'N/A'}\n")

    if len(bdfs) == 0:
        print("FAIL: BF3 expected but no BF3 device detected")
        return False

    result = run_command(
        "dmesg | grep -i -E "
        "'bluefield|bf3|dpu|connectx-7|firmware|pcie|aer|link|timeout|failed|failure|error|reset'"
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("PASS: No BF3 related error found in dmesg")
        return True

    issue_count = 0

    for line in result.stdout.strip().splitlines():
        lower_line = line.lower()

        related_to_bf3 = (
            any(bdf.lower() in lower_line for bdf in bdfs)
            or any(iface.lower() in lower_line for iface in interfaces)
            or "bluefield" in lower_line
            or "bf3" in lower_line
            or "dpu" in lower_line
            or "connectx-7" in lower_line
        )

        has_error_keyword = any(
            keyword in lower_line for keyword in ERROR_KEYWORDS
        )

        if related_to_bf3 and has_error_keyword:
            print(line)
            issue_count += 1

    print("\n==============================")

    if issue_count == 0:
        print("PASS: No BF3 related error found")
        return True
    else:
        print(f"WARNING: Found {issue_count} possible BF3 related log line(s)")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)