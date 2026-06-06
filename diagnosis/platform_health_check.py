import subprocess
import os
from datetime import datetime

LOG_DIR = "logs"

CHECKS = {
    "GPU Count": "gpu/gpu_count.py",
    "GPU Health": "gpu/gpu_health.py",
    "GPU PCIe": "gpu/gpu_pcie_check.py",
    "GPU XID": "gpu/gpu_xid_check.py",

    "E1.S Detection": "e1s/e1s_detect.py",
    "E1.S Speed": "e1s/e1s_speed_check.py",
    "E1.S Health": "e1s/e1s_health_check.py",

    "CX8 Count": "cx8/cx8_count.py",
    "CX8 Link": "cx8/cx8_link_status.py",
    "CX8 PCIe": "cx8/cx8_pcie_check.py",
    "CX8 Error": "cx8/cx8_error_check.py",

    "BF3 Detection": "bf3/bf3_detect.py",
    "BF3 PCIe": "bf3/bf3_pcie_check.py",
    "BF3 Network": "bf3/bf3_network_check.py",
    "BF3 Health": "bf3/bf3_health_check.py",

    "Sensor Count": "sensors/sensor_count.py",
    "Sensor Missing": "sensors/sensor_missing.py",
    "Sensor Health": "sensors/sensor_health.py",

    "PCIe Topology Compare": "pcie/compare_topology.py",
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

def print_status(name, status):
    print(f"{name:<25}: {status}")

def generate_summary(results):
    print("\n===== PLATFORM HEALTH SUMMARY =====\n")
    skip_items = [name for name, status in results.items() if status == "SKIP"]
    fail_items = [name for name, status in results.items() if status == "FAIL"]
    warning_items = [name for name, status in results.items() if status == "WARNING"]
    unknown_items = [name for name, status in results.items() if status == "UNKNOWN"]

    print(f"Total Checks : {len(results)}")
    print(f"PASS         : {list(results.values()).count('PASS')}")
    print(f"WARNING      : {len(warning_items)}")
    print(f"FAIL         : {len(fail_items)}")
    print(f"UNKNOWN      : {len(unknown_items)}")
    print(f"SKIP         : {len(skip_items)}")

    if skip_items:
        print("\nSkipped Items:")
        for item in skip_items:
            print(f"- {item}")

    if fail_items:
        print("\nFailed Items:")
        for item in fail_items:
            print(f"- {item}")

    if warning_items:
        print("\nWarning Items:")
        for item in warning_items:
            print(f"- {item}")

    print("\n===== ROOT CAUSE HINT =====\n")

    if "PCIe Topology Compare" in fail_items:
        print("Possible Root Cause:")
        print("- PCIe topology mismatch / missing device / upstream PCIe path issue")
        print("\nSuggested Action:")
        print("1. Review pcie/compare_topology.py output.")
        print("2. Compare current lspci tree with golden node.")
        print("3. Check if missing devices are in the same PCIe branch.")

    elif any(item.startswith("E1.S") for item in fail_items):
        print("Possible Root Cause:")
        print("- E1.S drive / slot / backplane / cable / PCIe path issue")
        print("\nSuggested Action:")
        print("1. Run diagnosis/e1s_speed_drop.py or diagnosis/e1s_drop_orchestrator.py.")
        print("2. Swap drive to check if issue follows drive or slot.")
        print("3. Check backplane/cable if issue follows slot.")

    elif any(item.startswith("CX8") for item in fail_items):
        print("Possible Root Cause:")
        print("- CX8 / OSFP / cable / peer port / IO board issue")
        print("\nSuggested Action:")
        print("1. Run diagnosis/cx8_link_down.py.")
        print("2. Check link state, cable, OSFP, and peer port.")
        print("3. Check CX8 PCIe and firmware.")

    elif any(item.startswith("GPU") for item in fail_items):
        print("Possible Root Cause:")
        print("- GPU / driver / PCIe / HGX baseboard issue")
        print("\nSuggested Action:")
        print("1. Check nvidia-smi and dmesg XID/SXID.")
        print("2. Run gpu/gpu_pcie_check.py.")
        print("3. Compare GPU PCIe path with good node.")

    elif any(item.startswith("BF3") for item in fail_items):
        print("Possible Root Cause:")
        print("- BF3 / DPU firmware / PCIe / network issue")
        print("\nSuggested Action:")
        print("1. Run diagnosis/bf3_failure.py.")
        print("2. Check BF3 firmware, PCIe link, and DPU OS status.")

    elif any(item.startswith("Sensor") for item in fail_items):
        print("Possible Root Cause:")
        print("- BMC / FRU / sensor mapping / hardware reporting issue")
        print("\nSuggested Action:")
        print("1. Run diagnosis/sensor_missing.py.")
        print("2. Check missing sensor list.")
        print("3. Compare with golden sensor list.")

    elif warning_items:
        print("Platform has warning items but no hard failure.")
        print("\nSuggested Action:")
        print("1. Review warning items.")
        print("2. Re-run failed production test if issue is intermittent.")
        print("3. Collect debug bundle if warning repeats.")

    else:
        print("PASS: Platform health looks good from current checks.")

def main():
    print("===== PLATFORM HEALTH CHECK =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{LOG_DIR}/platform_health_{timestamp}.txt"

    results = {}

    with open(log_file, "w") as log:
        log.write("===== PLATFORM HEALTH CHECK LOG =====\n")
        log.write(f"Generated Time: {timestamp}\n\n")

        for name, script in CHECKS.items():
            print(f"Running {name}...")
            output = run_script(script)
            status = analyze_output(output)
            results[name] = status

            print_status(name, status)

            log.write(f"\n===== {name} =====\n")
            log.write(f"Script: {script}\n\n")
            log.write(output)
            log.write("\n")

    print(f"\nFull log saved to: {log_file}")

    generate_summary(results)

if __name__ == "__main__":
    main()