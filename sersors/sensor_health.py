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
        lower_line = line.lower()

        if any(keyword in lower_line for keyword in BAD_KEYWORDS):
            print(line)
            issue_count += 1

    print("\n==============================")

    if issue_count == 0:
        print("PASS: All sensors look healthy")
    else:
        print(f"FAIL: Found {issue_count} possible sensor issue(s)")

if __name__ == "__main__":
    main()