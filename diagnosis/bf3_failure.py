import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

CHECKS = {
    "BF3 Detection": "bf3/bf3_detect.py",
    "BF3 Firmware": "bf3/bf3_fw_check.py",
    "BF3 Network": "bf3/bf3_network_check.py",
    "BF3 PCIe": "bf3/bf3_pcie_check.py",
    "BF3 Error": "bf3/bf3_error_check.py",
    "BF3 Health": "bf3/bf3_health_check.py",
    "PCIe Topology Compare": "pcie/compare_topology.py",
    "CX8 PCIe": "cx8/cx8_pcie_check.py",
    "GPU PCIe": "gpu/gpu_pcie_check.py",
    "Sensor Count": "sensors/sensor_count.py",
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
    if "SKIP" in text:
        return "SKIP"

    return "UNKNOWN"

def generate_suggestion(results):
    print("\n===== BF3 FAILURE DIAGNOSIS =====\n")

    bf3_detect = results.get("BF3 Detection")
    bf3_fw = results.get("BF3 Firmware")
    bf3_network = results.get("BF3 Network")
    bf3_pcie = results.get("BF3 PCIe")
    bf3_error = results.get("BF3 Error")
    bf3_health = results.get("BF3 Health")
    topology = results.get("PCIe Topology Compare")
    cx8_pcie = results.get("CX8 PCIe")
    gpu_pcie = results.get("GPU PCIe")
    sensor_count = results.get("Sensor Count")

    if bf3_detect == "FAIL" and topology == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 missing due to PCIe topology / upstream path issue")
        print("\nReason:")
        print("- BF3 detection failed and topology comparison also failed.")
        print("- This suggests BF3 may be missing at PCIe enumeration level.")
        print("\nSuggested Action:")
        print("1. Review pcie/compare_topology.py output.")
        print("2. Check whether BF3 BDF is missing compared with golden node.")
        print("3. Check BF3 seating, PCIe slot, riser, and upstream PCIe switch path.")
        print("4. Perform AC power cycle and re-check lspci.")

    elif bf3_detect == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 not detected / DPU enumeration issue")
        print("\nReason:")
        print("- BF3 detection check failed.")
        print("\nSuggested Action:")
        print("1. Check lspci | grep -i bluefield.")
        print("2. Check BF3 seating and PCIe slot.")
        print("3. Check BMC / DPU power status if available.")
        print("4. Power cycle the system and re-run detection.")

    elif bf3_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 PCIe link training / signal integrity issue")
        print("\nReason:")
        print("- BF3 PCIe link speed or width is below expected.")
        print("\nSuggested Action:")
        print("1. Check BF3 PCIe Gen/width from lspci -vv.")
        print("2. Compare with golden topology.")
        print("3. Check BF3 slot, riser, firmware, BIOS PCIe setting, and signal integrity.")

    elif bf3_fw == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 firmware mismatch or firmware update issue")
        print("\nReason:")
        print("- BF3 firmware check failed.")
        print("\nSuggested Action:")
        print("1. Check expected BF3 firmware version.")
        print("2. Re-run BF3 firmware update flow.")
        print("3. Check whether DPU OS update is stuck in a repeated update loop.")
        print("4. Confirm firmware definition file is correct.")

    elif bf3_network == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 network / DPU OS / dpudiag issue")
        print("\nReason:")
        print("- BF3 network check failed.")
        print("\nSuggested Action:")
        print("1. Check BF3 interface state and IP address.")
        print("2. Check ethtool output.")
        print("3. Run dpudiag if available.")
        print("4. If error shows 'DPU network diag failed with exit code 4', check DPU OS, BF3 FW, and PCIe interface traffic path.")

    elif bf3_error in ["FAIL", "WARNING"]:
        print("Possible Root Cause:")
        print("- BF3 driver / firmware / DPU runtime error")
        print("\nReason:")
        print("- BF3 related error logs were detected.")
        print("\nSuggested Action:")
        print("1. Review bf3/bf3_error_check.py output.")
        print("2. Look for BlueField, DPU, mlx5, firmware, timeout, reset, or PCIe AER errors.")
        print("3. Compare timestamp with production test failure.")
        print("4. Re-run BF3 debug bundle collection.")

    elif cx8_pcie == "FAIL" or gpu_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- Broader PCIe platform issue")
        print("\nReason:")
        print("- BF3 symptom appears together with CX8/GPU PCIe issue.")
        print("\nSuggested Action:")
        print("1. Compare full topology with golden node.")
        print("2. Check whether BF3 shares PCIe domain/branch with CX8/GPU.")
        print("3. Check PCIe switch, Bianca/mainboard, BIOS PCIe settings, and signal integrity.")

    elif sensor_count == "FAIL":
        print("Possible Root Cause:")
        print("- BMC / FRU / DPU sensor reporting issue")
        print("\nReason:")
        print("- Sensor count mismatch detected with BF3 symptom.")
        print("\nSuggested Action:")
        print("1. Run sensors/sensor_missing.py.")
        print("2. Check if missing sensors are BF3/DPU related.")
        print("3. Check BMC/HMC/FRU data.")

    elif bf3_health == "PASS":
        print("Result:")
        print("- BF3 health looks normal from current checks.")
        print("\nSuggested Action:")
        print("1. Re-run the original failing test.")
        print("2. Check whether the issue is intermittent.")
        print("3. Compare test failure timestamp with dmesg.")

    else:
        print("Result:")
        print("- BF3 failure diagnosis is inconclusive.")
        print("\nSuggested Action:")
        print("1. Run bf3/bf3_debug_bundle.py.")
        print("2. Run pcie/compare_topology.py.")
        print("3. Check BF3 firmware, DPU OS, PCIe, network, and dmesg manually.")

def main():
    print("===== BF3 FAILURE ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{LOG_DIR}/bf3_failure_{timestamp}.txt"

    results = {}

    with open(log_file, "w") as log:
        log.write("===== BF3 FAILURE DIAGNOSIS LOG =====\n")
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