import subprocess

BAD_KEYWORDS = [
    "cr",
    "nc",
    "nr",
    "critical",
    "non-critical",
    "not present",
    "unavailable",
    "failed",
    "error"
]

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def main():
    print("===== SENSOR HEALTH CHECK =====\n")

    result = run_command("ipmitool sdr elist")

    if result.returncode != 0:
        print("FAIL: Unable to execute ipmitool")
        print(result.stderr)
        return

    lines = result.stdout.splitlines()
    issue_count = 0

    for line in lines:
        if "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]

        if len(parts) < 3:
            continue

        sensor_name = parts[0]
        status = parts[2].lower()

        if status in BAD_KEYWORDS:
            print(f"{sensor_name}: {status}")
            issue_count += 1

    print("\n==============================")

    if issue_count == 0:
        print("PASS: All sensors look healthy")
    else:
        print(f"FAIL: Found {issue_count} possible sensor issue(s)")

if __name__ == "__main__":
    main()