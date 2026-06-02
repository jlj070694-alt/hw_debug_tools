import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

CHECKS = {
    "Sensor Count": "sensors/sensor_count.py",
    "Sensor Missing": "sensors/sensor_missing.py",
    "Sensor Health": "sensors/sensor_health.py",
    "PCIe Topology Compare": "pcie/compare_topology.py",
    "GPU Health": "gpu/gpu_health.py",
    "BF3 Health": "bf3/bf3_health_check.py",
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
    print("\n===== SENSOR MISSING DIAGNOSIS =====\n")

    sensor_count = results.get("Sensor Count")
    sensor_missing = results.get("Sensor Missing")
    sensor_health = results.get("Sensor Health")
    topology = results.get("PCIe Topology Compare")
    gpu_health = results.get("GPU Health")
    bf3_health = results.get("BF3 Health")

    if sensor_count == "FAIL" and sensor_missing == "FAIL":
        print("Possible Root Cause:")
        print("- Missing sensor definition / FRU / BMC / HMC mapping issue")
        print("\nReason:")
        print("- Sensor count mismatch detected.")
        print("- Missing sensor list is not matching golden sensor list.")
        print("\nSuggested Action:")
        print("1. Check missing sensor names from sensors/sensor_missing.py output.")
        print("2. Check BMC/HMC/FRU information.")
        print("3. Compare with a known good node.")
        print("4. If missing sensors are related to GPU/CX8/E1.S, check the related hardware path.")

    elif sensor_count == "FAIL" and topology == "FAIL":
        print("Possible Root Cause:")
        print("- Hardware device missing causing related sensors missing")
        print("\nReason:")
        print("- Sensor count mismatch and PCIe topology mismatch are both detected.")
        print("\nSuggested Action:")
        print("1. Check which PCIe device is missing.")
        print("2. Check whether missing sensors belong to that device.")
        print("3. Compare lspci -t with golden node.")

    elif sensor_health == "FAIL":
        print("Possible Root Cause:")
        print("- Sensor reading abnormal / threshold / device reporting issue")
        print("\nReason:")
        print("- Sensor exists but health check found abnormal status.")
        print("\nSuggested Action:")
        print("1. Review sensor_health output.")
        print("2. Check if sensor state is CR / NC / NR / Not Present.")
        print("3. Check related hardware or BMC sensor reading.")

    elif gpu_health == "FAIL":
        print("Possible Root Cause:")
        print("- GPU related sensor issue")
        print("\nReason:")
        print("- GPU health failed together with sensor issue.")
        print("\nSuggested Action:")
        print("1. Check GPU temperature/power/ECC.")
        print("2. Check GPU-related sensors.")
        print("3. Run nvidia-smi and compare with BMC sensor list.")

    elif bf3_health == "FAIL":
        print("Possible Root Cause:")
        print("- BF3 / DPU related sensor or PCIe issue")
        print("\nReason:")
        print("- BF3 health check failed together with sensor issue.")
        print("\nSuggested Action:")
        print("1. Check BF3 detection and PCIe status.")
        print("2. Check DPU OS / firmware.")
        print("3. Check BF3 related BMC sensors.")

    elif sensor_count == "PASS":
        print("Result:")
        print("- Sensor count looks normal.")
        print("\nSuggested Action:")
        print("1. If production test still fails, check sensor threshold or test script expectation.")
        print("2. Compare raw ipmitool output with test log.")

    else:
        print("Result:")
        print("- Sensor missing diagnosis is inconclusive.")
        print("\nSuggested Action:")
        print("1. Run sensors/sensor_report.py.")
        print("2. Compare with golden sensor list.")
        print("3. Check BMC/HMC/FRU data.")

def main():
    print("===== SENSOR MISSING ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{LOG_DIR}/sensor_missing_{timestamp}.txt"

    results = {}

    with open(log_file, "w") as log:
        log.write("===== SENSOR MISSING DIAGNOSIS LOG =====\n")
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