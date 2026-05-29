import os
import subprocess

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_cx8_interfaces():
    interfaces = []

    result = run_command("ls /sys/class/net")

    for iface in result.stdout.split():
        device_path = f"/sys/class/net/{iface}/device"

        if os.path.exists(device_path):
            vendor = run_command(f"cat {device_path}/vendor").stdout.strip()
            if vendor == "0x15b3":  # Mellanox/NVIDIA vendor ID
                interfaces.append(iface)

    return interfaces

def check_link_status(iface):
    result = run_command(f"cat /sys/class/net/{iface}/operstate")
    return result.stdout.strip()

def main():
    print("===== CX8 LINK STATUS CHECK =====")

    interfaces = get_cx8_interfaces()

    if not interfaces:
        print("FAIL: No CX8/Mellanox interfaces found")
        return

    overall_pass = True

    for iface in interfaces:
        status = check_link_status(iface)

        print(f"{iface}: {status}")

        if status != "up":
            print(f"WARNING: {iface} link is not up")
            overall_pass = False

    print("\n==============================")

    if overall_pass:
        print("PASS: All CX8 links are up")
    else:
        print("FAIL: One or more CX8 links are down")

if __name__ == "__main__":
    main()