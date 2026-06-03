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

from config.gb300_config import (
    EXPECTED_E1S_PCIE_SPEED,
    EXPECTED_E1S_PCIE_WIDTH
)

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_nvme_bdfs():
    result = run_command("lspci | grep -i 'Non-Volatile memory'")

    bdfs = []

    for line in result.stdout.strip().splitlines():
        bdf = line.split()[0]
        bdfs.append(bdf)

    return bdfs

def check_link_status(bdf):
    result = run_command(f"lspci -s {bdf} -vv")

    output = result.stdout

    lnkcap = re.search(r"LnkCap:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", output)
    lnksta = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", output)

    return lnkcap, lnksta

def main():
    print("===== E1.S SPEED CHECK =====\n")

    bdfs = get_nvme_bdfs()

    if not bdfs:
        print("FAIL: No NVMe device found")
        return

    overall_pass = True

    for bdf in bdfs:
        lnkcap, lnksta = check_link_status(bdf)

        print(f"Device: {bdf}")

        if not lnksta:
            print("FAIL: Cannot parse PCIe link status\n")
            overall_pass = False
            continue

        max_speed = lnkcap.group(1) if lnkcap else "Unknown"
        max_width = lnkcap.group(2) if lnkcap else "Unknown"

        current_speed = lnksta.group(1)
        current_width = lnksta.group(2)

        print(f"Max Link     : {max_speed} {max_width}")
        print(f"Current Link : {current_speed} {current_width}")

        if current_speed == EXPECTED_E1S_PCIE_SPEED and current_width == EXPECTED_E1S_PCIE_WIDTH:
            print("PASS: Link speed/width normal\n")
        else:
            print(
                f"FAIL: Speed drop detected. "
                f"Expected {EXPECTED_E1S_PCIE_SPEED} {EXPECTED_E1S_PCIE_WIDTH}, "
                f"but got {current_speed} {current_width}\n"
            )
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: All E1.S links are normal")
    else:
        print("FAIL: One or more E1.S drives have speed drop")

if __name__ == "__main__":
    main()