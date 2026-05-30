import subprocess
from datetime import datetime
import os

LOG_DIR = "logs"

CHECKS = {
    "E1.S Detection": "e1s/e1s_detect.py",
    "E1.S Speed": "e1s/e1s_speed_check.py",
    "E1.S PCIe": "e1s/e1s_pcie_check.py",
    "E1.S Health": "e1s/e1s_health_check.py",
    "CX8 Count": "cx8/cx8_count.py",
    "CX8 PCIe": "cx8/cx8_pcie_check.py",
    "GPU Count": "gpu/gpu_count.py",
    "GPU PCIe": "gpu/gpu_pcie_check.py",
    "Sensor Count": "sensors/sensor_count.py",
    "Sensor Missing": "sensors/sensor_missing.py",
    "BF3 Detection": "bf3/bf3_detect.py",
    "BF3 PCIe": "bf3/bf3_pcie_check.py",
}

def run_script(script_path):
    result = subprocess.run(
        ["python3", script_path],
        capture_output=True,
        text=True
    )

    output = result.stdout + "\n" + result.stderr
    return result.returncode, output

def analyze_output(output):
    text = output.upper()

    if "FAIL" in text:
        return "FAIL"
    elif "WARNING" in text:
        return "WARNING"
    elif "PASS" in text:
        return "PASS"
    else:
        return "UNKNOWN"

def print_result(name, status):
    if status == "PASS":
        print(f"[PASS]    {name}")
    elif status == "FAIL":
        print(f"[FAIL]    {name}")
    elif status == "WARNING":
        print(f"[WARNING] {name}")
    else:
        print(f"[UNKNOWN] {name}")

def generate_suggestion(results):
    print("\n===== ROOT CAUSE SUGGESTION =====\n")

    e1s_detect = results.get("E1.S Detection")
    e1s_speed = results.get("E1.S Speed")
    e1s_pcie = results.get("E1.S PCIe")
    cx8_count = results.get("CX8 Count")
    cx8_pcie = results.get("CX8 PCIe")
    gpu_count = results.get("GPU Count")
    gpu_pcie = results.get("GPU PCIe")
    sensor_count = results.get("Sensor Count")
    bf3_detect = results.get("BF3 Detection")
    bf3_pcie = results.get("BF3 PCIe")

    if e1s_detect == "FAIL" and cx8_count == "FAIL":
        print("Possible Root Cause:")
        print("- PCIe switch / Bianca / mainboard issue")
        print("\nReason:")
        print("- E1.S devices and CX8 devices are both abnormal.")
        print("- This suggests the issue may be upstream, not only the drive.")
        print("\nSuggested Action:")
        print("- Compare lspci tree with a good node.")
        print("- Check PCIe switch path.")
        print("- Consider Bianca/mainboard replacement if multiple downstream devices are missing.")

    elif e1s_detect == "FAIL" and cx8_count in ["PASS", "WARNING"]:
        print("Possible Root Cause:")
        print("- E1.S drive / slot / backplane / cable issue")
        print("\nReason:")
        print("- E1.S detection failed, but CX8 looks normal.")
        print("- This suggests the issue may be limited to the E1.S storage path.")
        print("\nSuggested Action:")
        print("- Swap the drive first.")
        print("- If issue follows the drive, replace the drive.")
        print("- If issue follows the slot, check backplane/cable/slot.")

    elif e1s_detect == "PASS" and (e1s_speed == "FAIL" or e1s_pcie == "FAIL"):
        print("Possible Root Cause:")
        print("- E1.S PCIe speed drop / signal integrity issue")
        print("\nReason:")
        print("- Drive is detected, but PCIe speed or width is below expected.")
        print("\nSuggested Action:")
        print("- Swap drive to confirm whether issue follows drive or slot.")
        print("- If issue follows slot, check backplane/cable.")
        print("- If multiple slots are affected, check PCIe switch or BIOS settings.")

    elif e1s_detect == "FAIL" and gpu_count == "FAIL":
        print("Possible Root Cause:")
        print("- Platform-level PCIe issue")
        print("\nReason:")
        print("- Both E1.S and GPU detection are abnormal.")
        print("\nSuggested Action:")
        print("- Check PCIe topology.")
        print("- Check BIOS PCIe configuration.")
        print("- Check mainboard / HGX baseboard connection.")

    elif sensor_count == "FAIL":
        print("Possible Root Cause:")
        print("- BMC / FRU / sensor mapping issue")
        print("\nReason:")
        print("- Sensor count mismatch detected.")
        print("\nSuggested Action:")
        print("- Run sensors/sensor_missing.py.")
        print("- Compare with golden sensor list.")
        print("- Check related FRU / BMC / HMC data.")

    elif bf3_detect == "FAIL" or bf3_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 / DPU PCIe issue")
        print("\nReason:")
        print("- BF3 detection or PCIe check failed.")
        print("\nSuggested Action:")
        print("- Check BF3 seating, firmware, PCIe link, and DPU OS status.")

    elif cx8_pcie == "FAIL" or gpu_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- Broader PCIe signal integrity or platform configuration issue")
        print("\nReason:")
        print("- CX8/GPU PCIe link issue detected together with E1.S symptom.")
        print("\nSuggested Action:")
        print("- Check PCIe link training.")
        print("- Compare with good node.")
        print("- Review BIOS and platform PCIe configuration.")

    else:
        print("No clear root cause found from current checks.")
        print("\nSuggested Action:")
        print("- Re-run the failing test.")
        print("- Run e1s/e1s_debug_bundle.py.")
        print("- Compare this node with a known good node.")
        print("- Check test log timestamp against dmesg.")

def main():
    print("===== E1.S DROP ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{LOG_DIR}/e1s_drop_orchestrator_{timestamp}.txt"

    results = {}

    with open(log_file, "w") as log:
        log.write("===== E1.S DROP ORCHESTRATOR LOG =====\n")
        log.write(f"Generated Time: {timestamp}\n\n")

        for name, script in CHECKS.items():
            print(f"Running {name}...")
            log.write(f"\n===== {name} =====\n")
            log.write(f"Script: {script}\n\n")

            returncode, output = run_script(script)
            status = analyze_output(output)

            results[name] = status
            print_result(name, status)

            log.write(output)
            log.write("\n")

    print(f"\nFull log saved to: {log_file}")

    generate_suggestion(results)

if __name__ == "__main__":
    main()