import subprocess
import re

EXPECTED_FW = "32.42.1000"   # 修改成你们当前标准版本

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def get_bf3_interfaces():

    result = run_command(
        "ip -o link show | awk -F': ' '{print $2}'"
    )

    interfaces = []

    for iface in result.stdout.splitlines():

        ethtool_result = run_command(
            f"ethtool -i {iface}"
        )

        if "mlx5_core" in ethtool_result.stdout:
            interfaces.append(iface)

    return interfaces

def main():

    print("===== BF3 FW CHECK =====\n")

    interfaces = get_bf3_interfaces()

    if not interfaces:
        print("FAIL: No BF3 interface found")
        return

    overall_pass = True

    for iface in interfaces:

        print(f"Interface: {iface}")

        result = run_command(
            f"ethtool -i {iface}"
        )

        fw_version = "Unknown"

        for line in result.stdout.splitlines():

            print(line)

            if "firmware-version:" in line:
                fw_version = line.split(":")[-1].strip()

        if EXPECTED_FW in fw_version:
            print("FW Check : PASS\n")
        else:
            print(
                f"FW Check : FAIL "
                f"(Expected {EXPECTED_FW})\n"
            )
            overall_pass = False

    print("==============================")

    if overall_pass:
        print("PASS: BF3 firmware check passed")
    else:
        print("FAIL: BF3 firmware mismatch detected")

if __name__ == "__main__":
    main()