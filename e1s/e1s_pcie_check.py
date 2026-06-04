# import subprocess
# import re

# EXPECTED_SPEED = "32GT/s"
# EXPECTED_WIDTH = "x4"

import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platfrom_config import load_config

cfg = load_config()

EXPECTED_E1S_PCIE_SPEED = cfg.EXPECTED_E1S_PCIE_SPEED
EXPECTED_E1S_PCIE_WIDTH = cfg.EXPECTED_E1S_PCIE_WIDTH

# from config.gb300_config import (
#     EXPECTED_E1S_PCIE_SPEED,
#     EXPECTED_E1S_PCIE_WIDTH
# )


def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_nvme_devices():
    result = run_command("lspci | grep -i 'Non-Volatile memory'")

    devices = []

    for line in result.stdout.strip().splitlines():
        bdf = line.split()[0]
        desc = " ".join(line.split()[1:])
        devices.append((bdf, desc))

    return devices

def parse_pcie_info(bdf):
    result = run_command(f"lspci -s {bdf} -vv")

    output = result.stdout

    lnkcap = re.search(
        r"LnkCap:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)",
        output
    )

    lnksta = re.search(
        r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)",
        output
    )

    return lnkcap, lnksta

def main():
    print("===== E1.S PCIE CHECK =====\n")

    devices = get_nvme_devices()

    if not devices:
        print("FAIL: No NVMe PCIe device found")
        return

    overall_pass = True

    for bdf, desc in devices:
        print(f"Device : {bdf}")
        print(f"Name   : {desc}")

        lnkcap, lnksta = parse_pcie_info(bdf)

        if not lnksta:
            print("FAIL: Cannot parse LnkSta\n")
            overall_pass = False
            continue

        cap_speed = lnkcap.group(1) if lnkcap else "Unknown"
        cap_width = lnkcap.group(2) if lnkcap else "Unknown"

        cur_speed = lnksta.group(1)
        cur_width = lnksta.group(2)

        print(f"Max Link     : {cap_speed} {cap_width}")
        print(f"Current Link : {cur_speed} {cur_width}")

        if cur_speed == EXPECTED_E1S_PCIE_SPEED and cur_width == EXPECTED_E1S_PCIE_WIDTH:
            print("PASS: PCIe link is normal\n")
        else:
            print("FAIL: PCIe link mismatch")
            print(f"Expected : {EXPECTED_E1S_PCIE_SPEED} {EXPECTED_E1S_PCIE_WIDTH}")
            print(f"Actual   : {cur_speed} {cur_width}")

            if cur_width != EXPECTED_E1S_PCIE_WIDTH:
                print("Hint     : Width drop may indicate slot, cable, backplane, or signal integrity issue")

            if cur_speed != EXPECTED_E1S_PCIE_SPEED:
                print("Hint     : Speed drop may indicate signal integrity, firmware, or platform config issue")

            print()
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: All E1.S PCIe links are normal")
    else:
        print("FAIL: One or more E1.S PCIe links have issue")

if __name__ == "__main__":
    main()