import subprocess

print("===== SYSTEM ENVIRONMENT CHECK =====")

print("\n[OS VERSION]")

os_cmd = "cat /etc/os-release"

os_result = subprocess.run(
    os_cmd,
    shell=True,
    capture_output=True,
    text=True
)
print(os_result.stdout)

print("[KERNEL VERSION]")

kernel_cmd = "uname -r"

kernel_result = subprocess.run(
    kernel_cmd,
    shell=True,
    capture_output=True,
    text=True
)
print(kernel_result.stdout)

print("\n[GPU CHECK]")

gpu_cmd = "lspci | grep -i nvidia"

gpu_result = subprocess.run(
    gpu_cmd,
    shell=True,
    capture_output=True,
    text=True
)

if gpu_result.stdout:
    print("PASS: NVIDIA GPU detected")
    print(gpu_result.stdout)
else:
    print("FAIL: No NVIDIA GPU detected")

print("[NVIDIA-SMI CHECK]")

nvsmi_result = subprocess.run(
    "which nvidia-smi",
    shell=True,
    capture_output=True,
    text=True
)

if nvsmi_result.returncode == 0:
    print("PASS: nvidia-smi found")
    print(nvsmi_result.stdout)
else:
    print("FAIL: nvidia-smi missing")
    print("ERROR:")
    print(nvsmi_result.stderr)