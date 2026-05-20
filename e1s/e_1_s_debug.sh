#!/bin/bash

# ============================================================
# E1.S Speed Drop Debug Automation
# Purpose:
#   Collect NVMe / PCIe evidence and detect E1.S speed or width drop
# Author: John Ji
# ============================================================

set -u

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HOSTNAME=$(hostname)
OUT_DIR="e1s_debug_${HOSTNAME}_${TIMESTAMP}"

mkdir -p "$OUT_DIR"

SUMMARY="$OUT_DIR/summary.txt"

EXPECTED_SPEED="16GT/s"
EXPECTED_WIDTH="x4"

print_header() {
    echo "============================================================" | tee -a "$SUMMARY"
    echo "$1" | tee -a "$SUMMARY"
    echo "============================================================" | tee -a "$SUMMARY"
}

collect_system_info() {
    print_header "System Information"
    {
        echo "Date: $(date)"
        echo "Hostname: $(hostname)"
        echo "Kernel: $(uname -a)"
        echo "User: $(whoami)"
    } | tee -a "$SUMMARY"
}

collect_basic_logs() {
    print_header "Collecting Basic Logs"

    nvme list > "$OUT_DIR/nvme_list.txt" 2>&1
    lspci -tv > "$OUT_DIR/lspci_tree.txt" 2>&1
    lspci > "$OUT_DIR/lspci_full.txt" 2>&1
    dmesg -T | egrep -i "nvme|pcie|aer|link|error|timeout|fatal|corrected|uncorrected" > "$OUT_DIR/dmesg_pcie_nvme.txt" 2>&1

    echo "Saved nvme_list.txt" | tee -a "$SUMMARY"
    echo "Saved lspci_tree.txt" | tee -a "$SUMMARY"
    echo "Saved lspci_full.txt" | tee -a "$SUMMARY"
    echo "Saved dmesg_pcie_nvme.txt" | tee -a "$SUMMARY"
}

find_nvme_devices() {
    lspci | grep -i "Non-Volatile" > "$OUT_DIR/nvme_bdf_list.txt" 2>&1
}

check_link_status() {
    print_header "E1.S / NVMe PCIe Link Status"

    if [ ! -s "$OUT_DIR/nvme_bdf_list.txt" ]; then
        echo "No NVMe PCIe devices found by lspci." | tee -a "$SUMMARY"
        return
    fi

    printf "%-15s %-20s %-20s %-15s\n" "BDF" "Expected" "Actual" "Result" | tee -a "$SUMMARY"
    printf "%-15s %-20s %-20s %-15s\n" "---" "--------" "------" "------" | tee -a "$SUMMARY"

    while read -r line; do
        BDF=$(echo "$line" | awk '{print $1}')
        DEVICE_DESC=$(echo "$line" | cut -d' ' -f2-)
        LINK_FILE="$OUT_DIR/${BDF}_link_status.txt"

        lspci -vv -s "$BDF" > "$OUT_DIR/${BDF}_lspci_vv.txt" 2>&1
        egrep "LnkCap:|LnkSta:" "$OUT_DIR/${BDF}_lspci_vv.txt" > "$LINK_FILE" 2>&1

        LNKCAP=$(grep "LnkCap:" "$LINK_FILE" | head -1)
        LNKSTA=$(grep "LnkSta:" "$LINK_FILE" | head -1)

        ACTUAL_SPEED=$(echo "$LNKSTA" | sed -n 's/.*Speed \([^,]*\).*/\1/p')
        ACTUAL_WIDTH=$(echo "$LNKSTA" | sed -n 's/.*Width \([^,]*\).*/\1/p')

        EXPECTED="${EXPECTED_SPEED} ${EXPECTED_WIDTH}"
        ACTUAL="${ACTUAL_SPEED} ${ACTUAL_WIDTH}"
        RESULT="PASS"

        if [ "$ACTUAL_SPEED" != "$EXPECTED_SPEED" ] || [ "$ACTUAL_WIDTH" != "$EXPECTED_WIDTH" ]; then
            RESULT="FAIL"
        fi

        printf "%-15s %-20s %-20s %-15s\n" "$BDF" "$EXPECTED" "$ACTUAL" "$RESULT" | tee -a "$SUMMARY"

        {
            echo ""
            echo "Device: $BDF $DEVICE_DESC"
            echo "$LNKCAP"
            echo "$LNKSTA"
            echo "Result: $RESULT"
        } >> "$SUMMARY"

    done < "$OUT_DIR/nvme_bdf_list.txt"
}

analyze_dmesg() {
    print_header "dmesg Error Keyword Summary"

    DMESG_FILE="$OUT_DIR/dmesg_pcie_nvme.txt"

    if [ ! -s "$DMESG_FILE" ]; then
        echo "No PCIe/NVMe related dmesg errors found." | tee -a "$SUMMARY"
        return
    fi

    echo "Potential error keywords:" | tee -a "$SUMMARY"

    for keyword in "AER" "Corrected" "Uncorrected" "fatal" "timeout" "reset" "link down" "I/O"; do
        COUNT=$(grep -i "$keyword" "$DMESG_FILE" | wc -l)
        echo "$keyword: $COUNT" | tee -a "$SUMMARY"
    done
}

root_cause_hint() {
    print_header "Root Cause Direction Hint"

    FAIL_COUNT=$(grep -c "FAIL" "$SUMMARY" || true)

    if [ "$FAIL_COUNT" -eq 0 ]; then
        echo "No speed/width drop detected in current snapshot." | tee -a "$SUMMARY"
        echo "If test still fails, compare with test log, slot mapping, and golden node." | tee -a "$SUMMARY"
    elif [ "$FAIL_COUNT" -eq 1 ]; then
        echo "Only one NVMe device shows link degradation." | tee -a "$SUMMARY"
        echo "Suggested next step: swap drive with a known-good slot." | tee -a "$SUMMARY"
        echo "If issue follows drive: suspect drive." | tee -a "$SUMMARY"
        echo "If issue stays with slot: suspect slot / cable / backplane / Bianca path." | tee -a "$SUMMARY"
    else
        echo "Multiple NVMe devices show link degradation." | tee -a "$SUMMARY"
        echo "Suggested next step: check if failed devices are under the same backplane or PCIe path." | tee -a "$SUMMARY"
        echo "Possible suspects: backplane, cable, retimer, PCIe switch, Bianca board, power/reset behavior." | tee -a "$SUMMARY"
    fi

    echo "" | tee -a "$SUMMARY"
    echo "Recommended manual checks:" | tee -a "$SUMMARY"
    echo "1. Swap drive and check if issue follows drive or stays with slot." | tee -a "$SUMMARY"
    echo "2. Compare lspci tree with a known-good node." | tee -a "$SUMMARY"
    echo "3. Check dmesg for AER / timeout / reset / link errors." | tee -a "$SUMMARY"
    echo "4. Try AC cycle or BMC power cycle if warm reboot behavior is suspicious." | tee -a "$SUMMARY"
}

main() {
    echo "Starting E1.S Speed Drop Debug Automation..."
    echo "Output folder: $OUT_DIR"

    collect_system_info
    collect_basic_logs
    find_nvme_devices
    check_link_status
    analyze_dmesg
    root_cause_hint

    echo ""
    echo "Done. Please check: $SUMMARY"
}

main
