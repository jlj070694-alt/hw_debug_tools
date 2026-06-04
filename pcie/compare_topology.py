import subprocess
import os
import re

GOLDEN_FILE = "pcie/golden/golden_topology.txt"

DEVICE_PATTERNS = {
    "NVMe": r"Non-Volatile memory",
    "CX8": r"ConnectX|Mellanox|NVIDIA.*Ethernet",
    "GPU": r"NVIDIA.*3D controller",
    "BF3": r"BlueField|BF3|DPU",
}

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def extract_section(text, section_name):
    pattern = rf"===== {re.escape(section_name)} =====\n.*?\n\n(.*?)(?=\n=====|\Z)"
    match = re.search(pattern, text, re.S)

    if match:
        return match.group(1)

    return ""

def extract_devices_from_lspci(text):
    devices = {}

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if not re.match(r"^[0-9a-fA-F:.]+", line):
            continue

        bdf = line.split()[0]
        desc = " ".join(line.split()[1:])

        for category, pattern in DEVICE_PATTERNS.items():
            if re.search(pattern, line, re.I):
                devices[bdf] = {
                    "category": category,
                    "desc": desc,
                    "line": line,
                    "domain": bdf.split(":")[0]
                }

    return devices

def load_golden_devices():
    if not os.path.exists(GOLDEN_FILE):
        print(f"FAIL: Golden topology file not found: {GOLDEN_FILE}")
        print("Please run collect_topology.py on a good node first.")
        return {}

    with open(GOLDEN_FILE, "r") as f:
        golden_text = f.read()

    full_lspci = extract_section(golden_text, "Full lspci")

    if not full_lspci:
        print("FAIL: Cannot find 'Full lspci' section in golden file")
        return {}

    return extract_devices_from_lspci(full_lspci)

def get_current_devices():
    result = run_command("lspci")
    return extract_devices_from_lspci(result.stdout)

def print_device_list(title, devices):
    print(f"\n===== {title} =====")

    if not devices:
        print("None")
        return

    for bdf, item in devices.items():
        print(f"{bdf:<15} {item['category']:<6} {item['desc']}")

def group_by_domain(devices):
    grouped = {}

    for bdf, item in devices.items():
        domain = item["domain"]

        if domain not in grouped:
            grouped[domain] = []

        grouped[domain].append((bdf, item))

    return grouped

def generate_suggestion(missing_devices):
    print("\n===== TOPOLOGY DIAGNOSIS SUGGESTION =====")

    if not missing_devices:
        print("PASS: No missing key PCIe devices compared with golden topology.")
        return

    grouped = group_by_domain(missing_devices)

    for domain, items in grouped.items():
        categories = set(item["category"] for _, item in items)

        print(f"\nDomain: {domain}")
        print(f"Missing Categories: {', '.join(sorted(categories))}")

        if "NVMe" in categories and "CX8" in categories:
            print("Possible Root Cause:")
            print("- Shared upstream PCIe switch / Bianca / mainboard issue")
            print("Reason:")
            print("- NVMe and CX8 devices are missing in the same PCIe domain.")
            print("Suggested Action:")
            print("- Compare lspci -t with the good node.")
            print("- Check PCIe switch path.")
            print("- Check Bianca/mainboard and related cables.")

        elif "NVMe" in categories:
            print("Possible Root Cause:")
            print("- E1.S drive / slot / backplane / cable issue")
            print("Reason:")
            print("- Only NVMe devices are missing in this domain.")
            print("Suggested Action:")
            print("- Swap drive first.")
            print("- If issue follows slot, check backplane/cable.")

        elif "CX8" in categories:
            print("Possible Root Cause:")
            print("- CX8 / IO board / cable / PCIe path issue")
            print("Reason:")
            print("- CX8 devices are missing in this domain.")
            print("Suggested Action:")
            print("- Check CX8 seating, IO board, OSFP, and PCIe link.")

        elif "GPU" in categories:
            print("Possible Root Cause:")
            print("- GPU / HGX baseboard / PCIe path issue")
            print("Reason:")
            print("- GPU devices are missing in this domain.")
            print("Suggested Action:")
            print("- Check nvidia-smi, GPU PCIe path, and HGX baseboard.")

        elif "BF3" in categories:
            print("Possible Root Cause:")
            print("- BF3 / DPU PCIe issue")
            print("Reason:")
            print("- BF3 device is missing.")
            print("Suggested Action:")
            print("- Check BF3 seating, firmware, PCIe link, and DPU OS status.")

        else:
            print("Possible Root Cause:")
            print("- Unknown PCIe topology mismatch")
            print("Suggested Action:")
            print("- Compare full lspci tree with good node.")

def main():
    print("===== PCIe TOPOLOGY COMPARE =====\n")

    golden_devices = load_golden_devices()
    current_devices = get_current_devices()

    if not golden_devices:
        return

    missing_bdfs = set(golden_devices.keys()) - set(current_devices.keys())
    extra_bdfs = set(current_devices.keys()) - set(golden_devices.keys())

    missing_devices = {
        bdf: golden_devices[bdf]
        for bdf in sorted(missing_bdfs)
    }

    extra_devices = {
        bdf: current_devices[bdf]
        for bdf in sorted(extra_bdfs)
    }

    print(f"Golden Key Device Count : {len(golden_devices)}")
    print(f"Current Key Device Count: {len(current_devices)}")

    print_device_list("MISSING DEVICES", missing_devices)
    print_device_list("EXTRA DEVICES", extra_devices)

    generate_suggestion(missing_devices)

if __name__ == "__main__":
    main()