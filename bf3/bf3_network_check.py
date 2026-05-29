import subprocess
import os

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_mlx_interfaces():
    interfaces = []

    result = run_command("ls /sys/class/net")

    for iface in result.stdout.split():
        device_path = f"/sys/class/net/{iface}/device"

        if os.path.exists(device_path):
            vendor = run_command(f"cat {device_path}/vendor").stdout.strip()

            if vendor == "0x15b3":
                interfaces.append(iface)

    return sorted(interfaces)

def get_operstate(iface):
    result = run_command(f"cat /sys/class/net/{iface}/operstate")
    return result.stdout.strip()

def get_ip_address(iface):
    result = run_command(f"ip -4 addr show {iface} | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){{3}}'")
    return result.stdout.strip()

def main():
    print("===== BF3 NETWORK CHECK =====\n")

    interfaces = get_mlx_interfaces()

    if not interfaces:
        print("FAIL: No BF3/Mellanox network interface found")
        return

    overall_pass = True

    print(f"{'Interface':<12} {'State':<10} {'IPv4 Address'}")
    print("-" * 40)

    for iface in interfaces:
        state = get_operstate(iface)
        ip_addr = get_ip_address(iface)

        if not ip_addr:
            ip_addr = "N/A"

        print(f"{iface:<12} {state:<10} {ip_addr}")

        if state != "up":
            overall_pass = False

    print("\n===== ETHTOOL SUMMARY =====")

    for iface in interfaces:
        print(f"\nInterface: {iface}")
        result = run_command(f"ethtool {iface}")

        if result.returncode != 0:
            print("FAIL: ethtool failed")
            print(result.stderr)
            overall_pass = False
            continue

        for line in result.stdout.splitlines():
            if (
                "Speed:" in line
                or "Duplex:" in line
                or "Link detected:" in line
                or "Auto-negotiation:" in line
            ):
                print(line)

    print("\n==============================")

    if overall_pass:
        print("PASS: BF3 network check passed")
    else:
        print("FAIL: One or more BF3 network interfaces have issue")

if __name__ == "__main__":
    main()