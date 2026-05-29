import subprocess
import re

EXPECTED_DRIVE_COUNT = 8
EXPECTED_SPEED = "32GT/s"
EXPECTED_WIDTH = "x4"

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_nvme_devices():
    result = run_command("nvme list")
    devices = []

    for line in result.stdout.splitlines():
        if line.startswith("/dev/nvme"):
            parts = line.split()
            dev = parts[0]
            serial = parts[1] if len(parts) > 1 else "Unknown"
            model = " ".join(parts[2:5]) if len(parts) > 4 else "Unknown"
            devices.append({"dev": dev, "serial": serial, "model": model})

    return devices

def get_bdf(dev):
    dev_name = dev.split("/")[-1]
    result = run_command(f"readlink -f /sys/block/{dev_name}/device")
    match = re.search(r"([0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7])", result.stdout)
    return match.group(1) if match else "Unknown"

def get_pcie_link(bdf):
    if bdf == "Unknown":
        return "Unknown", "Unknown"

    result = run_command(f"lspci -s {bdf} -vv")
    match = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", result.stdout)

    if match:
        return match.group(1), match.group(2)

    return "Unknown", "Unknown"

def main():
    print("===== E1.S HEALTH CHECK =====\n")

    devices = get_nvme_devices()
    detected_count = len(devices)
    overall_pass = True

    print(f"Expected Drive Count : {EXPECTED_DRIVE_COUNT}")
    print(f"Detected Drive Count : {detected_count}")

    if detected_count != EXPECTED_DRIVE_COUNT:
        print(f"FAIL: Expected {EXPECTED_DRIVE_COUNT}, but detected {detected_count}")
        overall_pass = False
    else:
        print("PASS: Drive count is correct")

    print("\n===== DRIVE HEALTH TABLE =====")
    print(f"{'Device':<15} {'BDF':<15} {'Speed':<10} {'Width':<8} {'Serial':<25} {'Status'}")
    print("-" * 95)

    for dev in devices:
        bdf = get_bdf(dev["dev"])
        speed, width = get_pcie_link(bdf)

        status = "PASS"

        if speed != EXPECTED_SPEED or width != EXPECTED_WIDTH:
            status = "FAIL"
            overall_pass = False

        print(
            f"{dev['dev']:<15} "
            f"{bdf:<15} "
            f"{speed:<10} "
            f"{width:<8} "
            f"{dev['serial']:<25} "
            f"{status}"
        )

    print("\n==============================")
    if overall_pass:
        print("PASS: E1.S health check passed")
    else:
        print("FAIL: E1.S health issue detected")

if __name__ == "__main__":
    main()