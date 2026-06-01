import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

COMMANDS = {
    "OS Version": "cat /etc/os-release",
    "Kernel Version": "uname -r",
    "PCIe Tree": "lspci -t",
    "Full lspci": "lspci",
    "NVMe Devices": "lspci | grep -i 'Non-Volatile memory'",
    "CX8 / Mellanox Devices": "lspci | grep -i -E 'ConnectX|Mellanox|NVIDIA.*Ethernet'",
    "GPU Devices": "lspci | grep -i -E 'NVIDIA.*H100|NVIDIA.*GPU|3D controller|VGA compatible controller'",
    "BF3 / BlueField Devices": "lspci | grep -i -E 'BlueField|BF3|DPU'",
    "NVMe List": "nvme list",
    "NVIDIA-SMI": "nvidia-smi -L",
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
    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(LOG_DIR, f"topology_report_{timestamp}.txt")

    with open(report_file, "w") as report:
        report.write("===== PCIe TOPOLOGY REPORT =====\n")
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

    print("PASS: PCIe topology report generated")
    print(f"Report file: {report_file}")

if __name__ == "__main__":
    main()