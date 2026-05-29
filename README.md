# HW Debug Tools

Hardware Debug Automation Toolkit for NVIDIA HGX / H100 / GB200 / GB300 Platforms

## Overview

HW Debug Tools is a collection of Python-based automation scripts designed to simplify hardware validation and debug workflows.

This project helps engineers quickly identify common hardware issues including:

* GPU Detection Failure
* GPU PCIe Link Issues
* GPU XID Errors
* E1.S Drive Missing
* E1.S Speed Drop
* CX8 Detection Issues
* CX8 Link Down
* Sensor Missing
* Sensor Health Issues

The goal is to reduce debug time and improve troubleshooting efficiency during manufacturing, validation, and bring-up activities.

---

## Project Structure

```text
hw_debug_tools/
│
├── debug.py
│
├── gpu/
│   ├── gpu_count.py
│   ├── gpu_health.py
│   ├── gpu_xid_check.py
│   └── gpu_pcie_check.py
│
├── e1s/
│   ├── e1s_detect.py
│   ├── e1s_speed_check.py
│   ├── e1s_pcie_check.py
│   ├── e1s_slot_mapping.py
│   ├── e1s_health_check.py
│   └── e1s_debug_bundle.py
│
├── cx8/
│   ├── cx8_count.py
│   ├── cx8_link_status.py
│   ├── cx8_mac_check.py
│   ├── cx8_pcie_check.py
│   ├── cx8_fw_check.py
│   └── cx8_error_check.py
│
├── sensors/
│   ├── sensor_count.py
│   ├── sensor_missing.py
│   ├── sensor_health.py
│   ├── sensor_compare.py
│   ├── sensor_report.py
│   └── expected_sensors.txt
│
└── logs/
```

---

## Features

### GPU Automation

* GPU Detection Check
* GPU Health Check
* GPU PCIe Link Verification
* GPU XID Error Collection

### E1.S Automation

* Drive Detection Check
* PCIe Speed Validation
* Slot Mapping
* Health Check
* Debug Bundle Collection

### CX8 Automation

* CX8 Detection Check
* Link Status Verification
* MAC Address Collection
* Firmware Version Check
* PCIe Link Validation
* Error Log Collection

### Sensor Automation

* Sensor Count Validation
* Missing Sensor Detection
* Sensor Health Check
* Good Node vs Bad Node Comparison
* Report Generation

---

## Usage

Launch the main menu:

```bash
python3 debug.py
```

Example:

```text
===== HW DEBUG TOOLS =====

1. GPU
2. E1S
3. CX8
4. Sensors

0. Exit
```

Select a category and run the desired automation script.

---

## Requirements

### Operating System

* RHEL 9.x
* Rocky Linux 9.x
* Ubuntu 22.04+
* Ubuntu 24.04+

### Required Packages

```bash
sudo dnf install pciutils ethtool ipmitool nvme-cli
```

or

```bash
sudo apt install pciutils ethtool ipmitool nvme-cli
```

### Python

```bash
python3 --version
```

Python 3.9 or later is recommended.

---

## Future Roadmap

* HTML Report Generation
* CSV Export
* Automatic Root Cause Analysis
* GUI Interface
* Web Dashboard
* Golden Node Comparison
* One-Click Debug Bundle Collection
* GB300 Validation Suite

---

## Author

Jialiang Ji

System Engineer

Focus Areas:

* NVIDIA HGX Systems
* H100 / GB200 / GB300 Validation
* Manufacturing Test Automation
* Hardware Debug Automation
* Python & Shell Scripting

