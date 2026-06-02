import os
import subprocess

DIAGNOSIS_FOLDER = "diagnosis"

MENU_ITEMS = {
    "1": {
        "name": "E1.S Drop / Missing Diagnosis",
        "script": "e1s_drop_orchestrator.py"
    },
    "2": {
        "name": "E1.S Speed Drop Diagnosis",
        "script": "e1s_speed_drop.py"
    },
    "3": {
        "name": "GPU Missing Diagnosis",
        "script": "gpu_missing.py"
    },
    "4": {
        "name": "CX8 Link Down Diagnosis",
        "script": "cx8_link_down.py"
    },
    "5": {
        "name": "Sensor Missing Diagnosis",
        "script": "sensor_missing.py"
    },
    "6": {
        "name": "BF3 Failure Diagnosis",
        "script": "bf3_failure.py"
    },
    "7": {
        "name": "Platform Health Check",
        "script": "platform_health_check.py"
    },
    "8": {
        "name": "Full Debug Bundle",
        "script": "full_debug_bundle.py"
    },
}

def run_script(script_name):
    script_path = os.path.join(DIAGNOSIS_FOLDER, script_name)

    if not os.path.exists(script_path):
        print(f"\nFAIL: Script not found: {script_path}")
        return

    print(f"\nRunning: {script_path}\n")

    subprocess.run(["python3", script_path])

def show_menu():
    print("\n===== HW DEBUG TOOLS - DIAGNOSIS MENU =====\n")

    for key, item in MENU_ITEMS.items():
        print(f"{key}. {item['name']}")

    print("0. Exit")

def main():
    while True:
        show_menu()

        choice = input("\nSelect: ").strip()

        if choice == "0":
            print("Exit diagnosis menu.")
            break

        if choice in MENU_ITEMS:
            run_script(MENU_ITEMS[choice]["script"])

            input("\nPress Enter to return to diagnosis menu...")
        else:
            print("Invalid selection")

if __name__ == "__main__":
    main()