import subprocess
import os
from datetime import datetime

REPORT_DIR = "logs"

COMMANDS = {
    "OS Version": "cat /etc/os-release",
    "Kernel Version": "uname -r",
    "BF3 PCIe Devices": "lspci | grep -i -E 'bluefield|bf3|dpu'",
    "BF3 PCIe Detail": "for bdf in $(lspci | grep -i -E 'bluefield|bf3|dpu' | awk '{print $1}'); do echo $bdf; lspci -s $bdf -vv; done",
    "Mellanox Interfaces": "for i in $(ls /sys/class/net); do if [ -e /sys/class/net/$i/device/vendor ]; then v=$(cat /sys/class/net/$i/device/vendor); if [ \"$v\" = \"0x15b3\" ]; then echo $i; fi; fi; done",
    "IP Link": "ip link",
    "IP Address": "ip addr",
    "Ethtool Info": "for i in $(ls /sys/class/net); do if [ -e /sys/class/net/$i/device/vendor ]; then v=$(cat /sys/class/net/$i/device/vendor); if [ \"$v\" = \"0x15b3\" ]; then echo ===== $i =====; ethtool -i $i; ethtool $i; fi; fi; done",
    "MST Status": "mst status",
    "Dmesg BF3 Errors": "dmesg | grep -i -E 'bluefield|bf3|dpu|mlx5|firmware|pcie|aer|link|timeout|failed|failure|error|reset'",
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
    os.makedirs(REPORT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(REPORT_DIR, f"bf3_debug_report_{timestamp}.txt")

    with open(report_file, "w") as report:
        report.write("===== BF3 DEBUG BUNDLE =====\n")
        report.write(f"Generated Time: {timestamp}\n\n")

        for title, command in COMMANDS.items():
            report.write(f"\n===== {title} =====\n")
            report.write(f"Command: {command}\n\n")

            stdout, stderr = run_command(command)

            if stdout:
                report.write(stdout)

            if stderr:
                report.write("\n[STDERR]\n")
                report.write(stderr)

            report.write("\n")

    print("PASS: BF3 debug bundle generated")
    print(f"Report file: {report_file}")

if __name__ == "__main__":
    main()