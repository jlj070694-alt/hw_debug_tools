import os
import importlib
import sys


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PLATFORM_CONFIG_MAP = {
    "GB300": "config.gb300_config",
    "GB200": "config.gb200_config",
    "H100": "config.h100_config",
    "B200": "config.b200_config",
}

def select_platform():
    platforms = {
        "1": "GB300",
        "2": "GB200",
        "3": "H100",
        "4": "B200",
    }

    print("\n===== SELECT PLATFORM =====")

    for key, value in platforms.items():
        print(f"{key}. {value}")

    choice = input("\nSelect platform: ").strip()

    platform = platforms.get(choice)

    if not platform:
        print("Invalid selection. Defaulting to GB300.")
        platform = "GB300"

    os.environ["HW_DEBUG_PLATFORM"] = platform

    return platform

def get_platform():
    platform = os.environ.get("HW_DEBUG_PLATFORM")

    if not platform:
        platform = select_platform()

    return platform

def load_config():

    platform = get_platform()

    module_name = PLATFORM_CONFIG_MAP[platform]

    config_file = os.path.join(
        PROJECT_ROOT,
        "config",
        f"{platform.lower()}_config.py"
    )

    sensor_file = os.path.join(
        PROJECT_ROOT,
        "sensors",
        "expected",
        f"{platform.lower()}_expected_sensors.txt"
    )

    missing_items = []

    if not os.path.exists(config_file):
        missing_items.append(config_file)

    if not os.path.exists(sensor_file):
        missing_items.append(sensor_file)

    if missing_items:

        print("\n===== PLATFORM CONFIG MISSING =====\n")

        print(f"Selected Platform: {platform}\n")

        print("Missing file(s):")

        for item in missing_items:
            print(f"  - {item}")

        print("\nPlease generate golden data on a known-good node:\n")

        if not os.path.exists(config_file):
            print(
                "1. Run:\n"
                "   python config/golden_config.py"
            )

        if not os.path.exists(sensor_file):
            print(
                "2. Run:\n"
                "   python sensors/collect_golden_sensor.py"
            )

        print(
            f"\nThen regenerate:\n"
            f"  {platform.lower()}_config.py\n"
            f"  {platform.lower()}_expected_sensors.txt"
        )

        sys.exit(1)

    return importlib.import_module(module_name)