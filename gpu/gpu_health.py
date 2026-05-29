import subprocess

def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return result

def main():

    print("===== GPU HEALTH CHECK =====\n")

    command = (
        "nvidia-smi "
        "--query-gpu=index,name,temperature.gpu,power.draw,"
        "ecc.errors.uncorrected.aggregate.total "
        "--format=csv,noheader,nounits"
    )

    result = run_command(command)

    if result.returncode != 0:
        print("FAIL: Unable to execute nvidia-smi")
        print(result.stderr)
        return

    lines = result.stdout.strip().splitlines()

    health_pass = True

    for line in lines:

        data = [x.strip() for x in line.split(",")]

        gpu_id = data[0]
        gpu_name = data[1]
        temperature = float(data[2])
        power = float(data[3])
        ecc = data[4]

        print(f"\nGPU {gpu_id}")
        print(f"Name        : {gpu_name}")
        print(f"Temperature : {temperature} C")
        print(f"Power       : {power} W")
        print(f"ECC Errors  : {ecc}")

        if temperature > 85:
            print("WARNING: High Temperature")
            health_pass = False

        if ecc != "0":
            print("WARNING: ECC Error Detected")
            health_pass = False

    print("\n==============================")

    if health_pass:
        print("PASS: GPU Health Check Passed")
    else:
        print("FAIL: GPU Health Issue Detected")

if __name__ == "__main__":
    main()