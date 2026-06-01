import re
import sys
import os

DEVICE_PATTERNS = {
    "NVMe": r"Non-Volatile memory",
    "CX8": r"ConnectX|Mellanox|NVIDIA.*Ethernet",
    "GPU": r"NVIDIA.*H100|NVIDIA.*GPU|3D controller|VGA compatible controller",
    "BF3": r"BlueField|BF3|DPU",
}

def extract_section(text, section_name):
    pattern = rf"===== {re.escape(section_name)} =====\n.*?\n\n(.*?)(?=\n=====|\Z)"
    match = re.search(pattern, text, re.S)

    if match:
        return match.group(1)

    return ""

def parse_lspci_devices(lspci_text):
    devices = []

    for line in lspci_text.splitlines():
        line = line.strip()

        if not line:
            continue

        if not re.match(r"^[0-9a-fA-F:.]+", line):
            continue

        bdf = line.split()[0]
        desc = " ".join(line.split()[1:])
        domain = bdf.split(":")[0]

        category = "Other"

        for name, pattern in DEVICE_PATTERNS.items():
            if re.search(pattern, line, re.I):
                category = name
                break

        if category != "Other":
            devices.append({
                "bdf": bdf,
                "domain": domain,
                "category": category,
                "desc": desc,
                "raw": line
            })

    return devices

def load_report(file_path):
    if not os.path.exists(file_path):
        print(f"FAIL: File not found: {file_path}")
        return ""

    with open(file_path, "r") as f:
        return f.read()

def print_summary(devices):
    print("===== PCIe TOPOLOGY PARSE SUMMARY =====\n")

    count_by_category = {}

    for device in devices:
        category = device["category"]

        if category not in count_by_category:
            count_by_category[category] = 0

        count_by_category[category] += 1

    print("Device Count:")
    for category, count in sorted(count_by_category.items()):
        print(f"{category:<8}: {count}")

    print("\n===== DEVICE LIST =====")
    print(f"{'BDF':<15} {'Domain':<8} {'Category':<8} Description")
    print("-" * 90)

    for device in devices:
        print(
            f"{device['bdf']:<15} "
            f"{device['domain']:<8} "
            f"{device['category']:<8} "
            f"{device['desc']}"
        )

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python3 pcie/parse_topology.py logs/topology_report_xxx.txt")
        return

    file_path = sys.argv[1]
    report_text = load_report(file_path)

    if not report_text:
        return

    full_lspci = extract_section(report_text, "Full lspci")

    if not full_lspci:
        print("FAIL: Cannot find 'Full lspci' section in topology report")
        return

    devices = parse_lspci_devices(full_lspci)

    print_summary(devices)

if __name__ == "__main__":
    main()