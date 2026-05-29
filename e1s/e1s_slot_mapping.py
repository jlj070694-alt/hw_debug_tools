import subprocess
import re

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_nvme_list():
    result = run_command("nvme list")

    devices = []

    for line in result.stdout.splitlines():
        if line.startswith("/dev/nvme"):
            parts = line.split()
            dev = parts[0]
            serial = parts[1] if len(parts) > 1 else "Unknown"
            model = " ".join(parts[2:5]) if len(parts) > 4 else "Unknown"
            devices.append({
                "dev": dev,
                "serial": serial,
                "model": model
            })

    return devices

def get_bdf(dev):
    result = run_command(f"readlink -f /sys/block/{dev.split('/')[-1]}/device")

    match = re.search(r"([0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7])", result.stdout)

    if match:
        return match.group(1)

    return "Unknown"

def main():
    print("===== E1.S SLOT MAPPING =====\n")

    devices = get_nvme_list()

    if not devices:
        print("FAIL: No NVMe device found")
        return

    print(f"{'Device':<15} {'BDF':<15} {'Serial':<25} {'Model'}")
    print("-" * 80)

    for item in devices:
        bdf = get_bdf(item["dev"])

        print(
            f"{item['dev']:<15} "
            f"{bdf:<15} "
            f"{item['serial']:<25} "
            f"{item['model']}"
        )

    print("\nPASS: E1.S mapping completed")

if __name__ == "__main__":
    main()