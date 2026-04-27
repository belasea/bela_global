import os
import shutil

# Define your possible root directories
windows_root = 'E:/Project/Others-Projects/HRM/hrms'
mac_root = '/Users/belase/project/office/website/bella_global/bella_global'

# List of directories to delete
directories_to_delete = ['__pycache__', 'migrations']

def delete_directories(root, directories):
    for dirpath, dirnames, filenames in os.walk(root):
        for dirname in dirnames:
            if dirname in directories:
                dir_to_delete = os.path.join(dirpath, dirname)
                print(f"Deleting directory: {dir_to_delete}")
                shutil.rmtree(dir_to_delete, ignore_errors=True)

if __name__ == "__main__":
    if os.path.exists(windows_root):
        delete_directories(windows_root, directories_to_delete)
        print("Deletion completed for Windows path.")
    elif os.path.exists(mac_root):
        delete_directories(mac_root, directories_to_delete)
        print("Deletion completed for Mac path.")
    else:
        print("No valid project directory found!")