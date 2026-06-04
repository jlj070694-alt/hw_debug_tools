# import subprocess
# import re

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

EXPECTED_BF3_PCIE_SPEED = cfg.EXPECTED_BF3_PCIE_SPEED
EXPECTED_BF3_PCIE_WIDTH = cfg.EXPECTED_BF3_PCIE_WIDTH

# from config.gb300_config import (
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

def get_bf3_bdfs():
    result = run_command("lspci | grep -i -E 'bluefield|bf3|dpu'")

    bdfs = []

    for line in result.stdout.strip().splitlines():
        bdf = line.split()[0]
        desc = " ".join(line.split()[1:])
        bdfs.append((bdf, desc))

    return bdfs

def parse_pcie_link(bdf):
    result = run_command(f"lspci -s {bdf} -vv")

    lnkcap = re.search(
        r"LnkCap:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)",
        result.stdout
    )

    lnksta = re.search(
        r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)",
        result.stdout
    )

    return lnkcap, lnksta

def main():
    print("===== BF3 PCIE CHECK =====\n")

    devices = get_bf3_bdfs()

    if not devices:
        print("FAIL: No BF3 / BlueField device found")
        return

    overall_pass = True

    for bdf, desc in devices:
        print(f"Device : {bdf}")
        print(f"Name   : {desc}")

        lnkcap, lnksta = parse_pcie_link(bdf)

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

        if cur_speed == EXPECTED_BF3_PCIE_SPEED and cur_width == EXPECTED_BF3_PCIE_WIDTH:
            print("PASS: BF3 PCIe link is normal\n")
        else:
            print("FAIL: BF3 PCIe link mismatch")
            print(f"Expected : {EXPECTED_BF3_PCIE_SPEED} {EXPECTED_BF3_PCIE_WIDTH}")
            print(f"Actual   : {cur_speed} {cur_width}")
            print("Hint     : Check BF3 slot, riser, BIOS PCIe setting, firmware, or signal integrity\n")
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: All BF3 PCIe links are normal")
    else:
        print("FAIL: One or more BF3 PCIe links have issue")

if __name__ == "__main__":
    main()