import os

print("===== SYSTEM ENVIRONMENT CHECK =====")

print("\n[OS VERSION]")
print(os.popen("cat /etc/os-release").read())

print("[KERNEL VERSION]")
print(os.popen("uname -r").read())

print("[GPU CHECK]")
gpu = os.popen("lspci | grep -i nvidia").read()

if gpu:
    print("PASS: NVIDIA GPU detected")
    print(gpu)
else:
    print("FAIL: No NVIDIA GPU detected")

print("[NVIDIA-SMI CHECK]")
nvsmi = os.popen("which nvidia-smi").read()

if nvsmi:
    print("PASS: nvidia-smi found")
else:
    print("FAIL: nvidia-smi missing")