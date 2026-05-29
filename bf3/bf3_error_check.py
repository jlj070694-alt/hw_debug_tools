import subprocess

ERROR_KEYWORDS = [
    "bluefield",
    "bf3",
    "dpu",
    "mlx5",
    "mlxconfig",
    "mst",
    "firmware",
    "pcie",
    "aer",
    "link down",
    "timeout",
    "failed",
    "failure",
    "error",
    "reset"
]

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def main():
    print("===== BF3 ERROR CHECK =====\n")

    command = (
        "dmesg | grep -i -E "
        "'bluefield|bf3|dpu|mlx5|firmware|pcie|aer|link|timeout|failed|failure|error|reset'"
    )

    result = run_command(command)

    if result.returncode != 0 or not result.stdout.strip():
        print("PASS: No BF3 related error found in dmesg")
        return

    lines = result.stdout.strip().splitlines()
    issue_count = 0

    for line in lines:
        lower_line = line.lower()

        if any(keyword in lower_line for keyword in ERROR_KEYWORDS):
            print(line)
            issue_count += 1

    print("\n==============================")

    if issue_count == 0:
        print("PASS: No BF3 related error found")
    else:
        print(f"WARNING: Found {issue_count} possible BF3 related log line(s)")

if __name__ == "__main__":
    main()