import subprocess

ERROR_KEYWORDS = [
    "xid",
    "sxid",
    "nvrm",
    "gpu has fallen off the bus",
    "gpu reset",
    "ecc",
    "nvlink",
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
    print("===== GPU XID / SXID CHECK =====\n")

    command = "dmesg | grep -i -E 'xid|sxid|nvrm|gpu|nvlink|ecc|timeout|failed|error'"

    result = run_command(command)

    if result.returncode != 0 or not result.stdout.strip():
        print("PASS: No GPU XID/SXID related error found in dmesg")
        return

    lines = result.stdout.strip().splitlines()
    error_count = 0

    for line in lines:
        lower_line = line.lower()

        if any(keyword in lower_line for keyword in ERROR_KEYWORDS):
            print(line)
            error_count += 1

    print("\n==============================")

    if error_count == 0:
        print("PASS: No GPU XID/SXID related error found")
    else:
        print(f"WARNING: Found {error_count} possible GPU related log lines")

if __name__ == "__main__":
    main()