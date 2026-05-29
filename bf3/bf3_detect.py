import subprocess

EXPECTED_BF3_COUNT = 1

def run_command(command):
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

def main():
    print("===== BF3 DETECTION CHECK =====\n")

    result = run_command("lspci | grep -i -E 'bluefield|bf3|dpu'")

    if result.returncode != 0 or not result.stdout.strip():
        print("FAIL: No BF3 / BlueField device detected")
        return

    bf3_lines = result.stdout.strip().splitlines()
    bf3_count = len(bf3_lines)

    print(f"Expected BF3 Count : {EXPECTED_BF3_COUNT}")
    print(f"Detected BF3 Count : {bf3_count}")

    print("\n===== BF3 DEVICE LIST =====")
    for line in bf3_lines:
        print(line)

    print("\n==============================")

    if bf3_count == EXPECTED_BF3_COUNT:
        print("PASS: BF3 detection check passed")
    else:
        print(f"FAIL: Expected {EXPECTED_BF3_COUNT}, but detected {bf3_count}")

if __name__ == "__main__":
    main()