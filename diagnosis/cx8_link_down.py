import os
import sys
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

CHECKS = {
    "CX8 Link Status": "cx8/cx8_link_status.py",
    "CX8 Count": "cx8/cx8_count.py",
    "CX8 PCIe Check": "cx8/cx8_pcie_check.py",
    "CX8 Firmware Check": "cx8/cx8_fw_check.py",
    "CX8 Error Check": "cx8/cx8_error_check.py",
    "PCIe Topology Compare": "pcie/compare_topology.py",
    "GPU PCIe Check": "gpu/gpu_pcie_check.py",
    "Sensor Count Check": "sensors/sensor_count.py",
}


def run_script(script_path):
    full_path = os.path.join(PROJECT_ROOT, script_path)

    result = subprocess.run(
        ["python3", full_path],
        capture_output=True,
        text=True
    )

    return result.stdout + "\n" + result.stderr


def analyze_output(output):
    text = output.upper()

    if "SKIP" in text:
        return "SKIP"

    if "FAIL" in text:
        return "FAIL"

    if "WARNING" in text:
        return "WARNING"

    if "PASS" in text:
        return "PASS"

    return "UNKNOWN"


def print_summary(results):
    print("\n===== CHECK SUMMARY =====\n")

    for status in ["PASS", "WARNING", "FAIL", "SKIP", "UNKNOWN"]:
        count = list(results.values()).count(status)
        print(f"{status:<8}: {count}")

    skipped_items = [
        name for name, status in results.items()
        if status == "SKIP"
    ]

    if skipped_items:
        print("\nSkipped Items:")
        for item in skipped_items:
            print(f"- {item}")


def generate_suggestion(results):
    print("\n===== CX8 LINK DOWN DIAGNOSIS =====\n")

    link_status = results.get("CX8 Link Status")
    cx8_count = results.get("CX8 Count")
    cx8_pcie = results.get("CX8 PCIe Check")
    cx8_fw = results.get("CX8 Firmware Check")
    cx8_error = results.get("CX8 Error Check")
    topology = results.get("PCIe Topology Compare")
    gpu_pcie = results.get("GPU PCIe Check")
    sensor_count = results.get("Sensor Count Check")

    if cx8_count == "SKIP":
        print("SKIP: CX8 link down diagnosis is skipped for this platform.")
        return

    if cx8_count == "FAIL":
        print("Possible Root Cause:")
        print("- CX8 not detected / PCIe enumeration issue")
        print("\nReason:")
        print("- CX8 count check failed.")
        print("- The OS may not be detecting one or more CX8 devices.")
        print("\nSuggested Action:")
        print("1. Compare PCIe topology with golden node.")
        print("2. Check CX8 seating / IO board / Bianca / PCIe switch path.")
        print("3. Power cycle the system and re-check lspci.")

    elif link_status == "FAIL" and cx8_pcie == "PASS":
        print("Possible Root Cause:")
        print("- Cable / OSFP / peer port / link partner issue")
        print("\nReason:")
        print("- CX8 device is detected and PCIe link looks normal.")
        print("- Network link is down, so issue is more likely external link path.")
        print("\nSuggested Action:")
        print("1. Swap loopback cable or OSFP module.")
        print("2. Test with known-good peer port.")
        print("3. Check original peer port and cable routing.")
        print("4. If issue follows cable/OSFP, replace cable/OSFP.")

    elif link_status == "FAIL" and cx8_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- CX8 PCIe path / signal integrity / IO board issue")
        print("\nReason:")
        print("- Both network link and PCIe link are abnormal.")
        print("\nSuggested Action:")
        print("1. Check CX8 PCIe speed/width.")
        print("2. Check IO board / riser / PCIe path.")
        print("3. Compare with good node topology.")
        print("4. Consider CX8 or board replacement if issue stays on same slot.")

    elif cx8_error in ["FAIL", "WARNING"]:
        print("Possible Root Cause:")
        print("- CX8 firmware / driver / signal integrity issue")
        print("\nReason:")
        print("- CX8 related error logs were found.")
        print("\nSuggested Action:")
        print("1. Review cx8_error_check output.")
        print("2. Look for Bad signal integrity / Negotiation failure / mlx5 errors.")
        print("3. Check firmware and driver version.")
        print("4. Re-run link test after reseating or replacing cable/OSFP.")

    elif cx8_fw == "FAIL":
        print("Possible Root Cause:")
        print("- CX8 firmware mismatch")
        print("\nReason:")
        print("- CX8 firmware check failed compared with golden config.")
        print("\nSuggested Action:")
        print("1. Check expected CX8 firmware in platform config.")
        print("2. Re-flash or update CX8 firmware if needed.")
        print("3. Re-run cx8/cx8_fw_check.py.")

    elif topology == "FAIL":
        print("Possible Root Cause:")
        print("- Upstream PCIe topology mismatch")
        print("\nReason:")
        print("- Current PCIe topology does not match golden topology.")
        print("\nSuggested Action:")
        print("1. Check which CX8 BDF is missing.")
        print("2. See whether missing CX8 shares branch with NVMe/GPU.")
        print("3. Check PCIe switch / Bianca / mainboard path.")

    elif gpu_pcie == "FAIL":
        print("Possible Root Cause:")
        print("- Platform-level PCIe issue")
        print("\nReason:")
        print("- CX8 symptom appears together with GPU PCIe issue.")
        print("\nSuggested Action:")
        print("1. Compare lspci -vv with good node.")
        print("2. Check BIOS PCIe configuration.")
        print("3. Check shared upstream switch or platform signal integrity.")

    elif sensor_count == "FAIL":
        print("Possible Root Cause:")
        print("- BMC / FRU / IO board sensor reporting issue")
        print("\nReason:")
        print("- Sensor count is abnormal together with CX8 issue.")
        print("\nSuggested Action:")
        print("1. Run sensors/sensor_missing.py.")
        print("2. Check IO board sensor / BMC / FRU mapping.")
        print("3. Confirm whether CX8 hardware is present from both OS and BMC.")

    elif link_status == "PASS":
        print("Result:")
        print("- CX8 link looks normal from current checks.")
        print("\nSuggested Action:")
        print("1. Re-run the failing test.")
        print("2. Check whether issue is intermittent.")
        print("3. Review peer side or test environment.")

    else:
        print("Result:")
        print("- CX8 link down diagnosis is inconclusive.")
        print("\nSuggested Action:")
        print("1. Run cx8/cx8_error_check.py.")
        print("2. Run pcie/compare_topology.py.")
        print("3. Check cable, OSFP, peer port, and CX8 firmware.")


def main():
    print("===== CX8 LINK DOWN ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"cx8_link_down_{timestamp}.txt")

    results = {}

    with open(log_file, "w") as log:
        log.write("===== CX8 LINK DOWN DIAGNOSIS LOG =====\n")
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

    print_summary(results)
    generate_suggestion(results)


if __name__ == "__main__":
    main()