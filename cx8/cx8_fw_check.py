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

            if vendor == "0x15b3":
                interfaces.append(iface)

    return sorted(interfaces)

def main():
    print("===== CX8 FIRMWARE CHECK =====\n")

    interfaces = get_cx8_interfaces()

    if not interfaces:
        print("FAIL: No CX8 interfaces found")
        return

    for iface in interfaces:
        print(f"\nInterface: {iface}")

        result = run_command(f"ethtool -i {iface}")

        if result.returncode != 0:
            print("FAIL: Cannot get firmware info")
            print(result.stderr)
            continue

        for line in result.stdout.splitlines():
            if "driver:" in line or "version:" in line or "firmware-version:" in line or "bus-info:" in line:
                print(line)

    print("\nPASS: CX8 firmware check completed")

if __name__ == "__main__":
    main()