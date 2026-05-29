# HW Debug Tools

Hardware Debug Automation Toolkit for NVIDIA HGX / H100 / GB200 / GB300 Platforms

## Overview

HW Debug Tools is a Python-based hardware validation and debug automation framework designed for AI server platforms.

The toolkit automates common troubleshooting tasks encountered during:

* Manufacturing Test
* Hardware Validation
* System Bring-up
* Production Debug
* Customer Support

Supported Platforms:

* NVIDIA HGX H100
* NVIDIA GB200
* NVIDIA GB300
* Supermicro AI Systems

---

## Features

### GPU Automation

* GPU Detection Check
* GPU Health Check
* GPU PCIe Link Check
* GPU XID/SXID Error Check

### E1.S Automation

* Drive Detection Check
* PCIe Speed Check
* PCIe Link Check
* Slot Mapping
* Health Check
* Debug Bundle Collection

### CX8 Automation

* CX8 Detection Check
* Link Status Check
* MAC Address Check
* Firmware Version Check
* PCIe Link Check
* Error Log Check

### BF3 Automation

* BF3 Detection Check
* BF3 Firmware Check
* BF3 Network Check
* BF3 PCIe Check
* BF3 Error Check
* BF3 Health Check
* BF3 Debug Bundle Collection

### Sensor Automation

* Sensor Count Check
* Missing Sensor Detection
* Sensor Health Check
* Good Node vs Bad Node Comparison
* Sensor Report Generation

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
├── bf3/
│   ├── bf3_detect.py
│   ├── bf3_fw_check.py
│   ├── bf3_network_check.py
│   ├── bf3_pcie_check.py
│   ├── bf3_error_check.py
│   ├── bf3_health_check.py
│   └── bf3_debug_bundle.py
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

## Usage

Launch the interactive debug menu:

```bash
python3 debug.py
```

Example:

```text
===== HW DEBUG TOOLS =====

1. GPU
2. E1S
3. CX8
4. BF3
5. Sensors

0. Exit
```

Select a category and execute the desired automation script.

---

## Requirements

### Operating Systems

* RHEL 9.x
* Rocky Linux 9.x
* Ubuntu 22.04
* Ubuntu 24.04

### Required Packages

```bash
dnf install pciutils ethtool ipmitool nvme-cli
```

or

```bash
apt install pciutils ethtool ipmitool nvme-cli
```

### Python

```bash
python3 --version
```

Recommended:

```text
Python 3.9+
```

---

## Example Use Cases

### E1.S Missing Drive

Expected:

```text
8 NVMe Drives
```

Detected:

```text
7 NVMe Drives
```

Automation:

```bash
python3 e1s/e1s_detect.py
```

---

### GPU PCIe Speed Drop

Expected:

```text
32GT/s x16
```

Detected:

```text
16GT/s x8
```

Automation:

```bash
python3 gpu/gpu_pcie_check.py
```

---

### Sensor Missing

Expected:

```text
116 Sensors
```

Detected:

```text
114 Sensors
```

Automation:

```bash
python3 sensors/sensor_missing.py
```

---

### BF3 Network Failure

Example Error:

```text
DPU network diag failed with exit code 4
```

Automation:

```bash
python3 bf3/bf3_network_check.py
```

---

## Future Roadmap

### Phase 2

* Automatic Root Cause Analysis
* HTML Report Generation
* CSV Report Export
* Log Parser Framework
* Platform Auto Detection

### Phase 3

* GUI Interface (Tkinter)
* Web Dashboard
* Golden Node Comparison
* AI-Assisted Debug Recommendation

---

## Author

Jialiang Ji

System Engineer

Specializing in:

* NVIDIA HGX Systems
* H100 / GB200 / GB300 Validation
* Manufacturing Test Automation
* Hardware Debug Automation
* Python & Linux Development
