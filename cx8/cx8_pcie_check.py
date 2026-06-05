import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.platform_config import load_config

cfg = load_config()

HAS_CX8 = getattr(cfg, "HAS_CX8", False)
EXPECTED_CX8_COUNT = cfg.EXPECTED_CX8_COUNT
EXPECTED_CX8_PCIE_SPEED = cfg.EXPECTED_CX8_PCIE_SPEED
EXPECTED_CX8_PCIE_WIDTH = cfg.EXPECTED_CX8_PCIE_WIDTH


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
            bdf = line.split()[0]
            bdfs.append(bdf)

    return bdfs


def check_pcie_link(bdf):
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
    print("===== CX8 PCIE CHECK =====\n")

    if not HAS_CX8:
        print("SKIP: This platform does not have CX8")
        return True    

    bdfs = get_cx8_bdfs()
    detected_count = len(bdfs)

    print(f"Expected CX8 Count : {EXPECTED_CX8_COUNT}")
    print(f"Detected CX8 Count : {detected_count}\n")

    if detected_count == 0:
        if EXPECTED_CX8_COUNT == 0:
            print("PASS: No CX8 expected on this platform")
            return
        else:
            print(
                f"FAIL: Expected {EXPECTED_CX8_COUNT} CX8 device(s), "
                f"but detected 0"
            )
            return

    if detected_count != EXPECTED_CX8_COUNT:
        print(
            f"WARNING: Expected {EXPECTED_CX8_COUNT} CX8 device(s), "
            f"but detected {detected_count}"
        )
        print("Continue checking detected CX8 PCIe links...\n")

    overall_pass = True

    for bdf in bdfs:
        lnkcap, lnksta = check_pcie_link(bdf)

        print(f"Device: {bdf}")

        if not lnksta:
            print("FAIL: Cannot parse LnkSta\n")
            overall_pass = False
            continue

        cap_speed = lnkcap.group(1) if lnkcap else "Unknown"
        cap_width = lnkcap.group(2) if lnkcap else "Unknown"

        cur_speed = lnksta.group(1)
        cur_width = lnksta.group(2)

        print(f"Max Link : {cap_speed} {cap_width}")
        print(f"Current  : {cur_speed} {cur_width}")

        if (
            cur_speed == EXPECTED_CX8_PCIE_SPEED
            and cur_width == EXPECTED_CX8_PCIE_WIDTH
        ):
            print("PASS: PCIe link is correct\n")
        else:
            print("FAIL: PCIe link mismatch")
            print(
                f"Expected : {EXPECTED_CX8_PCIE_SPEED} "
                f"{EXPECTED_CX8_PCIE_WIDTH}"
            )
            print(f"Actual   : {cur_speed} {cur_width}\n")
            overall_pass = False

    print("==============================")

    if overall_pass and detected_count == EXPECTED_CX8_COUNT:
        print("PASS: All CX8 PCIe links are correct")
    elif overall_pass and detected_count != EXPECTED_CX8_COUNT:
        print("FAIL: CX8 PCIe links look good, but CX8 count mismatch")
    else:
        print("FAIL: One or more CX8 PCIe links have issue")


if __name__ == "__main__":
    main()