# HW Debug Tools

Hardware Debug Automation and Diagnosis Toolkit for NVIDIA HGX Platforms

## Overview

HW Debug Tools is a Python-based hardware validation, debug automation, and diagnosis framework designed for AI server platforms.

The toolkit automates common troubleshooting tasks encountered during:

* Manufacturing Test
* Hardware Validation
* System Bring-Up
* Production Debug
* Customer Support

Supported Platforms:

* NVIDIA HGX H100
* NVIDIA B200
* NVIDIA GB200
* NVIDIA GB300

---

# Features

## Automation Modules

### GPU

* GPU Detection Check
* GPU Health Check
* GPU PCIe Check
* GPU XID/SXID Analysis

### E1.S

* Drive Detection Check
* Speed Check
* PCIe Check
* Slot Mapping
* Health Check
* Debug Bundle Collection

### CX8

* CX8 Detection Check
* Link Status Check
* MAC Address Check
* Firmware Check
* PCIe Check
* Error Analysis

### BF3

* BF3 Detection Check
* Firmware Check
* Network Check
* PCIe Check
* Error Analysis
* Health Check
* Debug Bundle Collection

### Sensors

* Sensor Count Check
* Missing Sensor Detection
* Sensor Health Check
* Sensor Comparison
* Sensor Report Generation

### PCIe

* PCIe Topology Collection
* PCIe Topology Parsing
* PCIe Topology Comparison
* Golden Topology Validation

---

# Diagnosis Engine

The Diagnosis Engine automatically combines multiple automation results and provides root cause suggestions.

Supported Diagnosis Workflows:

### E1.S Missing

```bash
python3 diagnosis/e1s_drop_orchestrator.py
```

Possible Root Causes:

* Drive Failure
* Slot Failure
* Backplane Failure
* Cable Failure
* PCIe Switch Failure
* Bianca/Mainboard Failure

---

### E1.S Speed Drop

```bash
python3 diagnosis/e1s_speed_drop.py
```

Possible Root Causes:

* Drive Speed Drop
* PCIe Link Width Drop
* Signal Integrity Issue
* Backplane Issue
* PCIe Switch Issue

---

### GPU Missing

```bash
python3 diagnosis/gpu_missing.py
```

Possible Root Causes:

* Driver Issue
* GPU PCIe Issue
* HGX Baseboard Issue
* PCIe Topology Issue

---

### CX8 Link Down

```bash
python3 diagnosis/cx8_link_down.py
```

Possible Root Causes:

* Cable Issue
* OSFP Issue
* Peer Port Issue
* CX8 PCIe Issue
* IO Board Issue

---

### BF3 Failure

```bash
python3 diagnosis/bf3_failure.py
```

Possible Root Causes:

* DPU OS Issue
* BF3 Firmware Issue
* PCIe Link Issue
* Network Issue
* PCIe Topology Issue

---

### Sensor Missing

```bash
python3 diagnosis/sensor_missing.py
```

Possible Root Causes:

* BMC Issue
* FRU Mapping Issue
* Missing Hardware Device
* Sensor Configuration Issue

---

### Platform Health Check

```bash
python3 diagnosis/platform_health_check.py
```

One-click platform validation:

* GPU
* E1.S
* CX8
* BF3
* Sensors
* PCIe Topology

---

# Project Structure

```text
hw_debug_tools/

├── debug.py
├── diagnosis.py

├── gpu/
├── e1s/
├── cx8/
├── bf3/
├── sensors/
├── pcie/

├── diagnosis/

│   ├── e1s_drop_orchestrator.py
│   ├── e1s_speed_drop.py
│   ├── gpu_missing.py
│   ├── cx8_link_down.py
│   ├── bf3_failure.py
│   ├── sensor_missing.py
│   ├── platform_health_check.py
│   └── full_debug_bundle.py

├── logs/

└── README.md
```

---

# User Interface

## Automation Menu

```bash
python3 debug.py
```

```text
1. GPU
2. E1.S
3. CX8
4. BF3
5. Sensors
6. PCIe
```

---

## Diagnosis Menu

```bash
python3 diagnosis.py
```

```text
1. E1.S Missing
2. E1.S Speed Drop
3. GPU Missing
4. CX8 Link Down
5. Sensor Missing
6. BF3 Failure
7. Platform Health Check
8. Full Debug Bundle
```

---

# Golden Topology System

Generate topology from a known good node:

```bash
python3 pcie/collect_topology.py
```

Save as:

```text
pcie/golden/golden_topology.txt
```

Compare against current node:

```bash
python3 pcie/compare_topology.py
```

This helps identify:

* Missing GPUs
* Missing NVMe Devices
* Missing CX8 Devices
* Missing BF3 Devices
* Shared PCIe Branch Failures

---

# Future Roadmap

## Phase 2

* Automatic Root Cause Scoring
* Confidence Level Calculation
* Topology Visualization
* HTML Report Generation
* CSV Export

## Phase 3

* Tkinter GUI
* Web Dashboard
* REST API
* Multi-Node Comparison
* Golden Node Database

## Phase 4

* AI-Assisted Diagnosis
* Automated Corrective Action Suggestions
* Historical Failure Pattern Learning

---

# Author

Jialiang Ji

System Engineer

Areas of Expertise:

* NVIDIA HGX Systems
* GB200 / GB300 Validation
* Manufacturing Test Automation
* Hardware Debug Automation
* Python Development
* Linux System Validation
