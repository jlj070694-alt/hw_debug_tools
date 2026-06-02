import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

CHECKS = {
    "E1.S Speed Check": "e1s/e1s_speed_check.py",
    "E1.S PCIe Check": "e1s/e1s_pcie_check.py",
    "E1.S Health Check": "e1s/e1s_health_check.py",
    "PCIe Topology Compare": "pcie/compare_topology.py",
    "CX8 PCIe Check": "cx8/cx8_pcie_check.py",
    "GPU PCIe Check": "gpu/gpu_pcie_check.py",
    "Sensor Count Check": "sensors/sensor_count.py",
}

def run_script(script_path):
    result = subprocess.run(
        ["python3", script_path],
        capture_output=True,
        text=True
    )
    return result.stdout + "\n" + result.stderr

def analyze_output(output):
    text = output.upper()

    if "FAIL" in text:
        return "FAIL"
    if "WARNING" in text:
        return "WARNING"
    if "PASS" in text:
        return "PASS"

    return "UNKNOWN"

def generate_suggestion(results):
    print("\n===== E1.S SPEED DROP DIAGNOSIS =====\n")

    e1s_speed = results.get("E1.S Speed Check")
    e1s_pcie = results.get("E1.S PCIe Check")
    e1s_health = results.get("E1.S Health Check")
    topology = results.get("PCIe Topology Compare")
    cx8_pcie = results.get("CX8 PCIe Check")
    gpu_pcie = results.get("GPU PCIe Check")
    sensor_count = results.get("Sensor Count Check")

    if e1s_speed == "FAIL" and e1s_pcie == "FAIL" and topology == "PASS":
        print("Possible Root Cause:")
        print("- E1.S drive / slot / backplane / cable issue")
        print("\nReason:")
        print("- E1.S speed/PCIe check failed.")
        print("- Topology comparison did not find missing upstream devices.")
        print("- Issue may be limited to E1.S storage path.")
        print("\nSuggested Action:")
        print("1. Swap the drive.")
        print("2. If issue follows the drive, replace the drive.")
        print("3. If issue follows the slot, replace/check backplane or cable.")

    elif e1s_speed == "FAIL" and topology == "FAIL":
        print("Possible Root Cause:")
        print("- PCIe topology / upstream switch / Bianca / mainboard issue")
        print("\nReason:")
        print("- E1.S speed drop detected.")
        print("- PCIe topology mismatch was also detected.")
        print("\nSuggested Action:")
        print("1. Compare current topology with golden node.")
        print("2. Check whether missing/down-trained E1.S shares branch with CX8/GPU.")
        print("3. Check PCIe switch path, Bianca, or mainboard.")

    elif e1s_speed == "FAIL" and (cx8_pcie == "FAIL" or gpu_pcie == "FAIL"):
        print("Possible Root Cause:")
        print("- Broader PCIe signal integrity / platform configuration issue")
        print("\nReason:")
        print("- E1.S has speed drop.")
        print("- CX8 or GPU PCIe also has abnormal link status.")
        print("\nSuggested Action:")
        print("1. Check PCIe training and BIOS PCIe settings.")
        print("2. Compare lspci -vv with good node.")
        print("3. Check upstream PCIe switch / board-level signal integrity.")

    elif e1s_health == "FAIL" and sensor_count == "FAIL":
        print("Possible Root Cause:")
        print("- BMC / FRU / sensor / platform reporting issue")
        print("\nReason:")
        print("- E1.S health failed and sensor count is also abnormal.")
        print("\nSuggested Action:")
        print("1. Run sensors/sensor_missing.py.")
        print("2. Check BMC/HMC/FRU data.")
        print("3. Confirm drive presence from both OS and BMC side.")

    elif e1s_speed == "PASS":
        print("Result:")
        print("- No E1.S speed drop detected by current automation.")
        print("\nSuggested Action:")
        print("1. Re-run the original failing test.")
        print("2. Check whether issue is intermittent.")
        print("3. Collect debug bundle if failure happens again.")

    else:
        print("Result:")
        print("- E1.S speed drop diagnosis is inconclusive.")
        print("\nSuggested Action:")
        print("1. Run e1s/e1s_debug_bundle.py.")
        print("2. Compare current topology with golden topology.")
        print("3. Check dmesg for NVMe / PCIe / AER errors.")

def main():
    print("===== E1.S SPEED DROP ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{LOG_DIR}/e1s_speed_drop_{timestamp}.txt"

    results = {}

    with open(log_file, "w") as log:
        log.write("===== E1.S SPEED DROP DIAGNOSIS LOG =====\n")
        log.write(f"Generated Time: {timestamp}\n\n")

        for name, script in CHECKS.items():
            print(f"Running {name}...")
            output = run_script(script)
            status = analyze_output(output)
            results[name] = status

            print(f"[{status}] {name}")

            log.write(f"\n===== {name} =====\n")
            log.write(f"Script: {script}\n\n")
            log.write(output)
            log.write("\n")

    print(f"\nFull log saved to: {log_file}")

    generate_suggestion(results)

if __name__ == "__main__":
    main()