import subprocess
import os
from datetime import datetime

REPORT_DIR = "logs"

COMMANDS = {
    "OS Version": "cat /etc/os-release",
    "Kernel Version": "uname -r",
    "NVMe List": "nvme list",
    "NVMe Smart Log": "for d in /dev/nvme*n1; do echo $d; nvme smart-log $d; done",
    "PCIe Tree": "lspci -t",
    "NVMe PCIe Devices": "lspci | grep -i 'Non-Volatile memory'",
    "NVMe Link Status": "for bdf in $(lspci | grep -i 'Non-Volatile memory' | awk '{print $1}'); do echo $bdf; lspci -s $bdf -vv | grep -E 'LnkCap|LnkSta'; done",
    "Dmesg NVMe Errors": "dmesg | grep -i -E 'nvme|pcie|aer|error|fail|timeout'",
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
    report_file = os.path.join(REPORT_DIR, f"e1s_debug_report_{timestamp}.txt")

    with open(report_file, "w") as report:
        report.write("===== E1.S DEBUG BUNDLE =====\n")
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

    print("PASS: E1.S debug bundle generated")
    print(f"Report file: {report_file}")

if __name__ == "__main__":
    main()