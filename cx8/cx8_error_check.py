import subprocess

ERROR_KEYWORDS = [
    "mlx5",
    "cx8",
    "connectx",
    "firmware",
    "link down",
    "bad signal integrity",
    "negotiation failure",
    "timeout",
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
    print("===== CX8 ERROR CHECK =====\n")

    result = run_command("dmesg | grep -i -E 'mlx5|connectx|cx8|firmware|link|error|failed|timeout'")

    if result.returncode != 0 or not result.stdout.strip():
        print("PASS: No CX8 related error found in dmesg")
        return

    lines = result.stdout.strip().splitlines()

    warning_count = 0

    for line in lines:
        lower_line = line.lower()

        if any(keyword in lower_line for keyword in ERROR_KEYWORDS):
            print(line)
            warning_count += 1

    print("\n==============================")

    if warning_count == 0:
        print("PASS: No CX8 related error found")
    else:
        print(f"WARNING: Found {warning_count} possible CX8 related log lines")

if __name__ == "__main__":
    main()