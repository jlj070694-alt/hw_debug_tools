import os
import importlib

PLATFORM_CONFIG_MAP = {
    "GB300": "config.gb300_config",
    "GB200": "config.gb200_config",
    "H100": "config.h100_config",
    "B200": "config.b200_config",
}

def get_platform():
    return os.environ.get("HW_DEBUG_PLATFORM", "GB300")

def load_config():
    platform = get_platform()

    if platform not in PLATFORM_CONFIG_MAP:
        raise ValueError(f"Unsupported platform: {platform}")

    return importlib.import_module(PLATFORM_CONFIG_MAP[platform])