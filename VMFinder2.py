import os
import shutil
from pathlib import Path

# Define the file extensions for virtual machine files
vm_extensions = ['.vmdk', '.vdi', '.vhd', '.vhdx', '.qcow2', '.vbox', '.iso', '.ova', '.ovf', '.xva', '.img', '.raw']

def find_vm_files(root_path):
    vm_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if any(file.endswith(ext) for ext in vm_extensions):
                vm_files.append(os.path.join(root, file))
    return vm_files

def move_files(files, target_path):
    for file in files:
        try:
            shutil.move(file, target_path)
            print(f"📁 Moved: {file} ➡️ {target_path}")
        except Exception as e:
            print(f"❌ Error moving {file}: {e}")

def main():
    print("💻🔍 Scanning for virtual machine files... 🕵️‍♂️💾")
    root_path = Path.home()
    vm_files = find_vm_files(root_path)
    
    if not vm_files:
        print("😢 No virtual machine files found.")
        return
    
    print(f"🔍 Found {len(vm_files)} virtual machine files! 🥳")
    target_path = input("📂 Enter the target path to move the files to: ")
    
    if not os.path.exists(target_path):
        print("❌ Target path does not exist. Please create it first.")
        return
    
    print("🚀 Moving files... 🛠️")
    move_files(vm_files, target_path)
    print("✅ All files moved successfully! 🎉")

if __name__ == "__main__":
    main()
