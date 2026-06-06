import os
import sys
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

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


def calculate_root_cause_score(results):
    scores = {
        "Drive Issue": 0,
        "Backplane / Cable / Slot Issue": 0,
        "PCIe Switch / Bianca / Mainboard Issue": 0,
        "Firmware / Driver / Test Environment Issue": 0,
        "BMC / Sensor / FRU Reporting Issue": 0,
    }

    e1s_speed = results.get("E1.S Speed Check")
    e1s_pcie = results.get("E1.S PCIe Check")
    e1s_health = results.get("E1.S Health Check")
    topology = results.get("PCIe Topology Compare")
    cx8_pcie = results.get("CX8 PCIe Check")
    gpu_pcie = results.get("GPU PCIe Check")
    sensor_count = results.get("Sensor Count Check")

    if e1s_speed == "FAIL":
        scores["Backplane / Cable / Slot Issue"] += 30
        scores["Drive Issue"] += 20

    if e1s_pcie == "FAIL":
        scores["Backplane / Cable / Slot Issue"] += 30
        scores["PCIe Switch / Bianca / Mainboard Issue"] += 20

    if e1s_health == "FAIL":
        scores["Drive Issue"] += 20
        scores["Backplane / Cable / Slot Issue"] += 20

    if topology == "FAIL":
        scores["PCIe Switch / Bianca / Mainboard Issue"] += 40

    if cx8_pcie == "FAIL":
        scores["PCIe Switch / Bianca / Mainboard Issue"] += 25

    if gpu_pcie == "FAIL":
        scores["PCIe Switch / Bianca / Mainboard Issue"] += 25

    if sensor_count == "FAIL":
        scores["BMC / Sensor / FRU Reporting Issue"] += 30

    if e1s_speed == "PASS" and e1s_pcie == "PASS":
        scores["Firmware / Driver / Test Environment Issue"] += 20

    return scores


def print_root_cause_score(scores):
    print("\n===== ROOT CAUSE SCORE =====\n")

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for cause, score in ranked:
        print(f"{cause:<45} {score}%")

    top_cause, top_score = ranked[0]

    print("\nMost Likely Root Cause:")
    print(f"- {top_cause} ({top_score}%)")

    return top_cause, top_score


def generate_suggestion(results):
    print("\n===== E1.S SPEED DROP DIAGNOSIS =====\n")

    if results.get("E1.S Speed Check") == "SKIP":
        print("SKIP: E1.S speed drop diagnosis is skipped for this platform.")
        return

    scores = calculate_root_cause_score(results)
    top_cause, top_score = print_root_cause_score(scores)

    print("\n===== SUGGESTED ACTION =====\n")

    if top_score == 0:
        print("No strong failure pattern detected.")
        print("1. Re-run the original failing test.")
        print("2. Check whether the issue is intermittent.")
        print("3. Collect debug bundle with e1s/e1s_debug_bundle.py.")
        return

    if top_cause == "Backplane / Cable / Slot Issue":
        print("1. Swap the E1.S drive first.")
        print("2. If issue follows the drive, replace the drive.")
        print("3. If issue follows the slot, check backplane / cable / slot.")
        print("4. Re-run e1s/e1s_speed_check.py after replacement.")

    elif top_cause == "Drive Issue":
        print("1. Swap with a known-good drive.")
        print("2. Check NVMe smart-log.")
        print("3. If issue follows drive, replace the drive.")

    elif top_cause == "PCIe Switch / Bianca / Mainboard Issue":
        print("1. Run pcie/compare_topology.py.")
        print("2. Compare lspci -t with a known-good node.")
        print("3. Check whether E1.S and CX8/GPU share the same missing PCIe branch.")
        print("4. If multiple downstream devices are affected, check PCIe switch / Bianca / mainboard.")

    elif top_cause == "BMC / Sensor / FRU Reporting Issue":
        print("1. Run sensors/sensor_missing.py.")
        print("2. Check BMC / HMC / FRU information.")
        print("3. Confirm drive presence from both OS and BMC side.")

    else:
        print("1. Re-run the failing test.")
        print("2. Check test environment and driver/firmware version.")
        print("3. Collect debug bundle with e1s/e1s_debug_bundle.py.")


def main():
    print("===== E1.S SPEED DROP ORCHESTRATOR =====\n")

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"e1s_speed_drop_{timestamp}.txt")

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

    print_summary(results)
    generate_suggestion(results)


if __name__ == "__main__":
    main()