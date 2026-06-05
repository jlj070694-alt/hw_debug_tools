import os
import importlib

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

    if platform not in PLATFORM_CONFIG_MAP:
        raise ValueError(
            f"Unsupported platform: {platform}"
        )

    return importlib.import_module(
        PLATFORM_CONFIG_MAP[platform]
    )