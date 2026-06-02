import subprocess
import re

EXPECTED_SPEED = "64GT/s"
EXPECTED_WIDTH = "x16"

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_gpu_bdfs():
    result = run_command("lspci | grep -i -E 'NVIDIA.*H100|NVIDIA.*GPU|3D controller|VGA compatible controller'")

    bdfs = []

    for line in result.stdout.strip().splitlines():
        bdf = line.split()[0]
        bdfs.append(bdf)

    return bdfs

def get_pcie_link(bdf):
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
    print("===== GPU PCIE CHECK =====\n")

    bdfs = get_gpu_bdfs()

    if not bdfs:
        print("FAIL: No NVIDIA GPU PCIe device found")
        return

    overall_pass = True

    for bdf in bdfs:
        lnkcap, lnksta = get_pcie_link(bdf)

        print(f"GPU BDF: {bdf}")

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

        if cur_speed == EXPECTED_SPEED and cur_width == EXPECTED_WIDTH:
            print("PASS: GPU PCIe link is normal\n")
        else:
            print("FAIL: GPU PCIe link mismatch")
            print(f"Expected : {EXPECTED_SPEED} {EXPECTED_WIDTH}")
            print(f"Actual   : {cur_speed} {cur_width}")
            print("Hint     : Check PCIe training, riser/baseboard, BIOS setting, or signal integrity\n")
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: All GPU PCIe links are normal")
    else:
        print("FAIL: One or more GPU PCIe links have issue")

if __name__ == "__main__":
    main()