import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

CHECKS = {
    "GPU Count": "gpu/gpu_count.py",
    "GPU Health": "gpu/gpu_health.py",
    "GPU PCIe": "gpu/gpu_pcie_check.py",
    "GPU XID": "gpu/gpu_xid_check.py",
    "PCIe Topology Compare": "pcie/compare_topology.py",
    "CX8 Count": "cx8/cx8_count.py",
    "E1.S Detection": "e1s/e1s_detect.py",
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

    return "UNKNOWN"

def generate_suggestion(results):
    print("\n===== GPU MISSING DIAGNOSIS =====\n")

    gpu_count = results.get("GPU Count")
    gpu_health = results.get("GPU Health")
    gpu_pcie = results.get("GPU PCIe")
    gpu_xid = results.get("GPU XID")
    topology = results.get("PCIe Topology Compare")
    cx8_count = results.get("CX8 Count")
    e1s_detect = results.get("E1.S Detection")
    sensor_count = results.get("Sensor Count")

    if gpu_count == "FAIL" and topology == "FAIL":
        print("Possible Root Cause:")
        print("- GPU missing due to PCIe topology / upstream path issue")
        print("\nReason:")
        print("- GPU count failed and topology comparison also failed.")
        print("- This suggests the GPU may be missing at PCIe enumeration level.")
        print("\nSuggested Action:")
        print("1. Review pcie/compare_topology.py output.")
        print("2. Check if GPU BDF is missing compared with golden node.")
        print("3. Check HGX baseboard / PCIe switch / mainboard path.")
        print("4. Perform AC power cycle and re-check lspci.")

    elif gpu_count == "FAIL" and gpu_pcie == "PASS":
        print("Possible Root Cause:")
        print("- NVIDIA driver / nvidia-smi recognition issue")
        print("\nReason:")
        print("- GPU PCIe looks normal, but GPU count check failed.")
        print("- Device may be visible in lspci but not initialized by NVIDIA driver.")
        print("\nSuggested Action:")
        print("1. Run nvidia-smi and check error message.")
        print("2. Check lsmod | grep nvidia.")
        print("3. Check dmesg | grep -i nvrm.")
        print("4. Reinstall/reload NVIDIA driver if needed.")

    elif gpu_count == "FAIL" and (cx8_count == "FAIL" or e1s_detect == "FAIL"):
        print("Possible Root Cause:")
        print("- Platform-level PCIe issue")
        print("\nReason:")
        print("- GPU missing together with CX8 or E1.S abnormality.")
        print("- Multiple device categories being abnormal suggests an upstream issue.")
        print("\nSuggested Action:")
        print("1. Compare full PCIe topology with golden node.")
        print("2. Check whether missing devices are in the same PCIe domain/branch.")
        print("3. Check PCIe switch, Bianca/mainboard, or HGX baseboard connection.")

    elif gpu_xid in ["FAIL", "WARNING"]:
        print("Possible Root Cause:")
        print("- GPU driver/runtime error or GPU instability")
        print("\nReason:")
        print("- XID/SXID related logs were detected.")
        print("\nSuggested Action:")
        print("1. Review gpu/gpu_xid_check.py output.")
        print("2. Check XID code and timestamp.")
        print("3. Check GPU temperature, ECC, PCIe, and NVLink status.")
        print("4. Re-run workload and compare with dmesg.")

    elif gpu_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- GPU PCIe link training / signal integrity issue")
        print("\nReason:")
        print("- GPU PCIe speed or width is below expected.")
        print("\nSuggested Action:")
        print("1. Check GPU PCIe Gen/width from lspci -vv.")
        print("2. Compare with golden node.")
        print("3. Check PCIe switch / HGX baseboard / BIOS PCIe settings.")

    elif sensor_count == "FAIL":
        print("Possible Root Cause:")
        print("- GPU-related sensor / BMC / HMC reporting issue")
        print("\nReason:")
        print("- Sensor count mismatch detected with GPU symptom.")
        print("\nSuggested Action:")
        print("1. Run sensors/sensor_missing.py.")
        print("2. Check if missing sensors are GPU related.")
        print("3. Check BMC/HMC/FRU data.")

    elif gpu_count == "PASS":
        print("Result:")
        print("- GPU count looks normal.")
        print("\nSuggested Action:")
        print("1. If production test still reports GPU missing, check test environment.")
        print("2. Compare nvidia-smi -L with test log timestamp.")
        print("3. Check intermittent PCIe or driver reset errors.")

    else:
        print("Result:")
        print("- GPU missing diagnosis is inconclusive.")
        print("\nSuggested Action:")
        print("1. Run gpu/gpu_xid_check.py.")
        print("2. Run pcie/compare_topology.py.")
        print("3. Check nvidia-smi, lspci, and dmesg manually.")

def main():
    print("===== GPU MISSING ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{LOG_DIR}/gpu_missing_{timestamp}.txt"

    results = {}

    with open(log_file, "w") as log:
        log.write("===== GPU MISSING DIAGNOSIS LOG =====\n")
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