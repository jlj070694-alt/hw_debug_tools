import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

COMMANDS = {
    "OS Version": "cat /etc/os-release",
    "Kernel Version": "uname -r",
    "Hostname": "hostname",
    "Uptime": "uptime",

    "Full PCIe Tree": "lspci -t",
    "Full lspci": "lspci",
    "PCIe Verbose Key Devices": (
        "for bdf in $(lspci | grep -i -E "
        "'Non-Volatile memory|ConnectX|Mellanox|NVIDIA|BlueField|BF3|DPU' "
        "| awk '{print $1}'); do echo ===== $bdf =====; lspci -s $bdf -vv; done"
    ),

    "NVIDIA-SMI": "nvidia-smi",
    "NVIDIA-SMI GPU List": "nvidia-smi -L",
    "NVIDIA-SMI Topology": "nvidia-smi topo -m",

    "NVMe List": "nvme list",
    "NVMe Smart Log": "for d in /dev/nvme*n1; do echo ===== $d =====; nvme smart-log $d; done",

    "CX8 / Mellanox Devices": "lspci | grep -i -E 'ConnectX|Mellanox|NVIDIA.*Ethernet'",
    "Mellanox Interfaces": (
        "for i in $(ls /sys/class/net); do "
        "if [ -e /sys/class/net/$i/device/vendor ]; then "
        "v=$(cat /sys/class/net/$i/device/vendor); "
        "if [ \"$v\" = \"0x15b3\" ]; then echo $i; fi; "
        "fi; done"
    ),
    "IP Link": "ip link",
    "IP Address": "ip addr",
    "Ethtool Mellanox Info": (
        "for i in $(ls /sys/class/net); do "
        "if [ -e /sys/class/net/$i/device/vendor ]; then "
        "v=$(cat /sys/class/net/$i/device/vendor); "
        "if [ \"$v\" = \"0x15b3\" ]; then "
        "echo ===== $i =====; ethtool -i $i; ethtool $i; "
        "fi; fi; done"
    ),

    "BF3 / BlueField Devices": "lspci | grep -i -E 'BlueField|BF3|DPU'",
    "MST Status": "mst status",

    "Sensor List": "ipmitool sdr elist",
    "FRU Info": "ipmitool fru",
    "BMC LAN Info": "ipmitool lan print",

    "Dmesg Key Errors": (
        "dmesg | grep -i -E "
        "'nvme|pcie|aer|xid|sxid|nvrm|mlx5|bluefield|bf3|dpu|sensor|timeout|failed|failure|error|reset|link down'"
    ),
}

def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr

def main():
    print("===== FULL DEBUG BUNDLE COLLECTION =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(LOG_DIR, f"full_debug_bundle_{timestamp}.txt")

    with open(report_file, "w") as report:
        report.write("===== FULL DEBUG BUNDLE =====\n")
        report.write(f"Generated Time: {timestamp}\n\n")

        for title, command in COMMANDS.items():
            print(f"Collecting {title}...")

            report.write(f"\n===== {title} =====\n")
            report.write(f"Command: {command}\n\n")

            stdout, stderr = run_command(command)

            if stdout:
                report.write(stdout)

            if stderr:
                report.write("\n[STDERR]\n")
                report.write(stderr)

            report.write("\n")

    print("\nPASS: Full debug bundle generated")
    print(f"Report file: {report_file}")

if __name__ == "__main__":
    main()