import os, shutil

root_path = './C3_T1_random50/'
target_root_path = './C3-T1-Raw'
n = 0
for home, dirs, files, in os.walk(root_path):
    for file_name in files:
        if 'nii.gz' in file_name:
            print(home, dirs, file_name)
            source_path = os.path.join(home, file_name)
            target_path = os.path.join(target_root_path, file_name)
            shutil.copyfile(source_path, target_path)
            n += 1
            print(n)