import subprocess
import os
import re

CONFIG_DIR = "config"

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def ask_platform():
    platforms = {
        "1": "gb300",
        "2": "gb200",
        "3": "h100",
        "4": "b200",
    }

    print("\n===== SELECT PLATFORM =====")
    for key, value in platforms.items():
        print(f"{key}. {value.upper()}")

    choice = input("\nSelect platform: ").strip()
    return platforms.get(choice, "gb300")

def get_gpu_count():
    result = run_command("nvidia-smi -L")
    return len([l for l in result.stdout.splitlines() if l.startswith("GPU ")])

def get_gpu_pcie():
    result = run_command(
        "lspci | grep -i 'NVIDIA' | grep -i '3D controller'"
    )

    for line in result.stdout.splitlines():
        bdf = line.split()[0]
        detail = run_command(f"lspci -s {bdf} -vv").stdout

        match = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", detail)

        if match:
            return match.group(1), match.group(2)

    return "Unknown", "Unknown"

def get_e1s_count():
    result = run_command("nvme list")
    return len([l for l in result.stdout.splitlines() if l.startswith("/dev/nvme")])

def get_e1s_pcie():
    result = run_command("lspci | grep -i 'Non-Volatile memory'")

    for line in result.stdout.splitlines():
        bdf = line.split()[0]
        detail = run_command(f"lspci -s {bdf} -vv").stdout

        match = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", detail)

        if match:
            return match.group(1), match.group(2)

    return "Unknown", "Unknown"

def get_cx8_count():
    result = run_command(
        "lspci | grep -i 'Ethernet controller' | grep -i 'ConnectX-8'"
    )
    return len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0

def get_cx8_pcie():
    result = run_command(
        "lspci | grep -i 'Ethernet controller' | grep -i 'ConnectX-8'"
    )

    for line in result.stdout.splitlines():
        bdf = line.split()[0]
        detail = run_command(f"lspci -s {bdf} -vv").stdout

        match = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", detail)

        if match:
            return match.group(1), match.group(2)

    return "Unknown", "Unknown"

def get_bf3_count():
    result = run_command("lspci | grep -i -E 'BlueField|BF3|DPU'")
    return len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0

def get_bf3_pcie():
    result = run_command("lspci | grep -i -E 'BlueField|BF3|DPU'")

    for line in result.stdout.splitlines():
        bdf = line.split()[0]
        detail = run_command(f"lspci -s {bdf} -vv").stdout

        match = re.search(r"LnkSta:.*Speed ([0-9.]+GT/s).*Width (x[0-9]+)", detail)

        if match:
            return match.group(1), match.group(2)

    return "Unknown", "Unknown"

def get_sensor_count():
    result = run_command("ipmitool sdr elist")
    return len([l for l in result.stdout.splitlines() if "|" in l])

def write_config(platform, data):
    os.makedirs(CONFIG_DIR, exist_ok=True)

    file_path = os.path.join(CONFIG_DIR, f"{platform}_config.py")

    with open(file_path, "w") as f:
        f.write("# ==========================================\n")
        f.write(f"# Auto-generated golden config for {platform.upper()}\n")
        f.write("# Generated from known-good node\n")
        f.write("# ==========================================\n\n")

        f.write(f'PLATFORM_NAME = "{platform.upper()}"\n\n')

        f.write("# GPU\n")
        f.write(f"EXPECTED_GPU_COUNT = {data['gpu_count']}\n")
        f.write(f'EXPECTED_GPU_PCIE_SPEED = "{data["gpu_speed"]}"\n')
        f.write(f'EXPECTED_GPU_PCIE_WIDTH = "{data["gpu_width"]}"\n\n')

        f.write("# E1.S\n")
        f.write(f"EXPECTED_E1S_COUNT = {data['e1s_count']}\n")
        f.write(f'EXPECTED_E1S_PCIE_SPEED = "{data["e1s_speed"]}"\n')
        f.write(f'EXPECTED_E1S_PCIE_WIDTH = "{data["e1s_width"]}"\n\n')

        f.write("# CX8\n")
        f.write(f"EXPECTED_CX8_COUNT = {data['cx8_count']}\n")
        f.write(f'EXPECTED_CX8_PCIE_SPEED = "{data["cx8_speed"]}"\n')
        f.write(f'EXPECTED_CX8_PCIE_WIDTH = "{data["cx8_width"]}"\n\n')

        f.write("# BF3\n")
        f.write(f"EXPECTED_BF3_COUNT = {data['bf3_count']}\n")
        f.write(f'EXPECTED_BF3_PCIE_SPEED = "{data["bf3_speed"]}"\n')
        f.write(f'EXPECTED_BF3_PCIE_WIDTH = "{data["bf3_width"]}"\n\n')

        f.write("# Sensors\n")
        f.write(f"EXPECTED_SENSOR_COUNT = {data['sensor_count']}\n")

    print(f"\nPASS: Golden config generated: {file_path}")

def main():
    print("===== GOLDEN CONFIG GENERATOR =====")
    print("Run this script only on a known-good node.\n")

    platform = ask_platform()

    data = {}

    print("Collecting GPU config...")
    data["gpu_count"] = get_gpu_count()
    data["gpu_speed"], data["gpu_width"] = get_gpu_pcie()

    print("Collecting E1.S config...")
    data["e1s_count"] = get_e1s_count()
    data["e1s_speed"], data["e1s_width"] = get_e1s_pcie()

    print("Collecting CX8 config...")
    data["cx8_count"] = get_cx8_count()
    data["cx8_speed"], data["cx8_width"] = get_cx8_pcie()

    print("Collecting BF3 config...")
    data["bf3_count"] = get_bf3_count()
    data["bf3_speed"], data["bf3_width"] = get_bf3_pcie()

    print("Collecting Sensor config...")
    data["sensor_count"] = get_sensor_count()

    print("\n===== COLLECTED GOLDEN CONFIG =====")
    for key, value in data.items():
        print(f"{key}: {value}")

    confirm = input("\nGenerate config file? (yes/no): ").strip().lower()

    if confirm == "yes":
        write_config(platform, data)
    else:
        print("Canceled.")

if __name__ == "__main__":
    main()