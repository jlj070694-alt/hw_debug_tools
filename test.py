print("Hello GB300")

gpu_name = "GPU0"

temp = 85

speed = 640.5

print(gpu_name)

print(temp)

print(speed)

driver_name = "E1.S"

driver_speed = 32

driver_status = "x16"

print("driver_name:",driver_name,driver_speed,driver_status)

if temp > 80:
    print("overheat")

if temp > 90:
    print("overheat")
else:
    print("Normal")


if temp > 85:
    print("Critial")
elif temp >=70:
    print("Warning")
else:
    print("Normal")



gpus = ["GPU0","GPU1","GPU2","GPU3"]

for gpu in gpus:
    print(gpu)

temps = [80,70,81,90]

i = 0
for t in temps:
    if t > 80:
        print("GPU",i,"Hot GPU")
        i+=1
    else:
        i+=1

def check_temp(temp):
    if temp >80:
        return "Hot"
    return "Normal"
result = check_temp(81)

print(result)

def check_drive_speed(speed):
    if speed<1000:
        return "Speed drop"
    return "Normal"

result = check_drive_speed(999)

print(result)


gpu = {
    "name": "GPU0",
    "temp": 85
}
print(gpu["name"],gpu["temp"])



temps = [70, 85, 90, 60]

for temp in temps:
    print("GPU temp ->",temp,"->",check_temp(temp))

def check_nvme(expected_nvme):
    detected_nvme = 7
    if expected_nvme==detected_nvme:
        return "PASS: NVMe count is correct"
    else:
        return "FAIL: Expected ", expected_nvme,"NVMe, but detected ", detected_nvme

result= check_nvme(8)


print(result)