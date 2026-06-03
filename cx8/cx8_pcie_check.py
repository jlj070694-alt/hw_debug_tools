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

from config.gb300_config import (
    EXPECTED_CX8_PCIE_SPEED,
    EXPECTED_CX8_PCIE_WIDTH
)

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_cx8_bdfs():
    result = run_command("lspci | grep -i -E 'ConnectX|Mellanox|NVIDIA.*Ethernet'")
    
    bdfs = []
    for line in result.stdout.strip().splitlines():
        bdf = line.split()[0]
        bdfs.append(bdf)

    return bdfs

def check_pcie_link(bdf):
    result = run_command(f"lspci -s {bdf} -vv")

    output = result.stdout

    lnkcap = re.search(r"LnkCap:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", output)
    lnksta = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", output)

    return lnkcap, lnksta, output

def main():
    print("===== CX8 PCIE CHECK =====\n")

    bdfs = get_cx8_bdfs()

    if not bdfs:
        print("FAIL: No CX8 device found")
        return

    overall_pass = True

    for bdf in bdfs:
        lnkcap, lnksta, _ = check_pcie_link(bdf)

        print(f"Device: {bdf}")

        if not lnksta:
            print("FAIL: Cannot parse LnkSta")
            overall_pass = False
            continue

        cap_speed = lnkcap.group(1) if lnkcap else "Unknown"
        cap_width = lnkcap.group(2) if lnkcap else "Unknown"

        cur_speed = lnksta.group(1)
        cur_width = lnksta.group(2)

        print(f"Max Link : {cap_speed} {cap_width}")
        print(f"Current  : {cur_speed} {cur_width}")

        if cur_speed == EXPECTED_CX8_PCIE_SPEED and cur_width == EXPECTED_CX8_PCIE_WIDTH:
            print("PASS: PCIe link is correct\n")
        else:
            print(
                f"FAIL: PCIe link mismatch. "
                f"Expected {EXPECTED_CX8_PCIE_SPEED} {EXPECTED_CX8_PCIE_WIDTH}, "
                f"but got {cur_speed} {cur_width}\n"
            )
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: All CX8 PCIe links are correct")
    else:
        print("FAIL: One or more CX8 PCIe links have issue")

if __name__ == "__main__":
    main()