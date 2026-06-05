# import subprocess
# import os
# import re

# EXPECTED_BF3_COUNT = 1
# EXPECTED_SPEED = "32GT/s"
# EXPECTED_WIDTH = "x16"

import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from config.platform_config import load_config

cfg = load_config()

EXPECTED_BF3_COUNT = cfg.EXPECTED_BF3_COUNT
EXPECTED_BF3_PCIE_SPEED = cfg.EXPECTED_BF3_PCIE_SPEED
EXPECTED_BF3_PCIE_WIDTH = cfg.EXPECTED_BF3_PCIE_WIDTH

# from config.gb300_config import (
#     EXPECTED_BF3_COUNT,
#     EXPECTED_BF3_PCIE_SPEED,
#     EXPECTED_BF3_PCIE_WIDTH
# )

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def check_detect():
    result = run_command("lspci | grep -i -E 'bluefield|bf3|dpu'")
    lines = result.stdout.strip().splitlines()

    if len(lines) == EXPECTED_BF3_COUNT:
        return True, f"PASS: Detected {len(lines)} BF3 device(s)"
    elif len(lines) == 0:
        return False, "FAIL: No BF3 device detected"
    else:
        return False, f"FAIL: Expected {EXPECTED_BF3_COUNT}, detected {len(lines)}"

def check_pcie():
    result = run_command("lspci | grep -i -E 'bluefield|bf3|dpu'")
    devices = result.stdout.strip().splitlines()

    if not devices:
        return False, "FAIL: Cannot check PCIe because no BF3 device was found"

    messages = []
    overall_pass = True

    for line in devices:
        bdf = line.split()[0]
        detail = run_command(f"lspci -s {bdf} -vv").stdout

        match = re.search(
            r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)",
            detail
        )

        if not match:
            messages.append(f"{bdf}: FAIL: Cannot parse LnkSta")
            overall_pass = False
            continue

        speed = match.group(1)
        width = match.group(2)

        if speed == EXPECTED_BF3_PCIE_SPEED and width == EXPECTED_BF3_PCIE_WIDTH:
            messages.append(f"{bdf}: PASS: PCIe {speed} {width}")
        else:
            messages.append(
                f"{bdf}: FAIL: PCIe mismatch. "
                f"Expected {EXPECTED_BF3_PCIE_SPEED} {EXPECTED_BF3_PCIE_WIDTH}, got {speed} {width}"
            )
            overall_pass = False

    return overall_pass, "\n".join(messages)

def get_mlx_interfaces():
    interfaces = []

    result = run_command("ls /sys/class/net")

    for iface in result.stdout.split():
        device_path = f"/sys/class/net/{iface}/device"

        if os.path.exists(device_path):
            vendor = run_command(f"cat {device_path}/vendor").stdout.strip()

            if vendor == "0x15b3":
                interfaces.append(iface)

    return sorted(interfaces)

def check_network():
    interfaces = get_mlx_interfaces()

    if not interfaces:
        return False, "FAIL: No BF3/Mellanox network interface found"

    messages = []
    overall_pass = True

    for iface in interfaces:
        state = run_command(f"cat /sys/class/net/{iface}/operstate").stdout.strip()

        if state == "up":
            messages.append(f"{iface}: PASS: Link is up")
        else:
            messages.append(f"{iface}: WARNING: Link state is {state}")
            overall_pass = False

    return overall_pass, "\n".join(messages)

def check_errors():
    result = run_command(
        "dmesg | grep -i -E "
        "'bluefield|bf3|dpu|mlx5|firmware|pcie|aer|link|timeout|failed|failure|error|reset'"
    )

    if result.returncode != 0 or not result.stdout.strip():
        return True, "PASS: No BF3 related error found in dmesg"

    lines = result.stdout.strip().splitlines()
    issue_lines = []

    for line in lines:
        lower = line.lower()
        if any(k in lower for k in [
            "bluefield", "bf3", "dpu", "mlx5", "firmware",
            "pcie", "aer", "timeout", "failed", "failure",
            "error", "reset"
        ]):
            issue_lines.append(line)

    if issue_lines:
        return False, "\n".join(issue_lines)

    return True, "PASS: No BF3 related error found"

def main():
    print("===== BF3 HEALTH CHECK =====\n")

    if EXPECTED_BF3_COUNT == 0:
        print("SKIP: This platform does not have BF3")
        print("PASS: BF3 health check skipped")
        return

    checks = {
        "Detection": check_detect,
        "PCIe": check_pcie,
        "Network": check_network,
        "Error Log": check_errors,
    }

    overall_pass = True

    for name, func in checks.items():
        print(f"\n[{name}]")
        passed, message = func()
        print(message)

        if not passed:
            overall_pass = False

    print("\n==============================")

    if overall_pass:
        print("PASS: BF3 health check passed")
    else:
        print("FAIL: BF3 health issue detected")

if __name__ == "__main__":
    main()