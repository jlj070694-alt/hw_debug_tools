import subprocess
import re

XID_TABLE = {
    13: "Graphics Engine Error",
    31: "MMU Fault",
    43: "GPU Stopped Processing",
    48: "ECC Error",
    63: "ECC Page Retirement",
    79: "GPU Fallen Off Bus",
    94: "NVLink Error",
    95: "NVLink Error",
    110: "Security Fault",
    119: "GSP Error",
    120: "GSP Error",
    140: "GPU Memory Error",
    143: "NVLink Training Failure",
    163: "HW Thermal Slowdown",
}

SXID_TABLE = {
    # for future sxid
}

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def extract_xid(line):
    match = re.search(r"Xid.*?:\s*(\d+)", line, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return None

def extract_sxid(line):
    match = re.search(r"SXid.*?:\s*(\d+)", line, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return None

def print_xid_analysis(line):
    xid = extract_xid(line)

    if xid is None:
        return False

    description = XID_TABLE.get(xid, "Unknown NVIDIA XID")

    print("--------------------------------")
    print(f"Type        : XID")
    print(f"Code        : {xid}")
    print(f"Description : {description}")
    print(f"Log         : {line}")

    return True

def print_sxid_analysis(line):
    sxid = extract_sxid(line)

    if sxid is None:
        return False

    description = SXID_TABLE.get(sxid, "Unknown NVIDIA SXID / NVSwitch event")

    print("--------------------------------")
    print(f"Type        : SXID")
    print(f"Code        : {sxid}")
    print(f"Description : {description}")
    print(f"Log         : {line}")

    return True

def main():
    print("===== GPU XID / SXID CHECK =====\n")

    command = "dmesg | grep -i -E 'NVRM: Xid|SXid'"

    result = run_command(command)

    if result.returncode != 0 or not result.stdout.strip():
        print("PASS: No GPU XID/SXID found in dmesg")
        return

    lines = result.stdout.strip().splitlines()

    xid_count = 0
    sxid_count = 0
    unknown_count = 0

    for line in lines:
        if print_xid_analysis(line):
            xid_count += 1
        elif print_sxid_analysis(line):
            sxid_count += 1
        else:
            print("--------------------------------")
            print("Type        : UNKNOWN")
            print(f"Log         : {line}")
            unknown_count += 1

    print("\n==============================")
    print(f"XID Count     : {xid_count}")
    print(f"SXID Count    : {sxid_count}")
    print(f"Unknown Count : {unknown_count}")

    if xid_count > 0 or sxid_count > 0:
        print("\nFAIL: GPU XID/SXID detected")
    else:
        print("\nPASS: No valid XID/SXID detected")

if __name__ == "__main__":
    main()