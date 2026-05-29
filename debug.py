import os
import subprocess

def run_script(script_path):
    print(f"\nRunning {script_path}...\n")

    subprocess.run(
        ["python3", script_path]
    )

def get_scripts(folder):

    scripts = []

    for file in os.listdir(folder):

        if file.endswith(".py") and file != "__init__.py":
            scripts.append(file)

    return sorted(scripts)

def submenu(folder):

    while True:

        scripts = get_scripts(folder)

        print(f"\n===== {folder.upper()} MENU =====")

        for idx, script in enumerate(scripts, start=1):
            print(f"{idx}. {script}")

        print("0. Back")

        choice = input("\nSelect: ")

        if choice == "0":
            break

        try:
            selected_script = scripts[int(choice)-1]

            script_path = os.path.join(folder, selected_script)

            run_script(script_path)

        except:
            print("Invalid selection")

def main():

    folders = [
        "cx8",
        "e1s",
        "gpu",
        "nccl",
        "sensors"
    ]

    while True:

        print("\n===== HW DEBUG TOOLS =====\n")

        for idx, folder in enumerate(folders, start=1):
            print(f"{idx}. {folder.upper()}")

        print("0. Exit")

        choice = input("\nSelect: ")

        if choice == "0":
            print("Goodbye")
            break

        try:

            selected_folder = folders[int(choice)-1]

            submenu(selected_folder)

        except:
            print("Invalid selection")

if __name__ == "__main__":
    main()