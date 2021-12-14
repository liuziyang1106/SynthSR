import os,shutil

root_path = "/data/ziyang/workspace/respo_fork/SynthSR/C3-T1-Raw/"
target_path = "/data/ziyang/workspace/respo_fork/SynthSR/C3-T1-SR/"

for file_name in os.listdir(root_path):
    new_file_name = file_name.replace('.nii.gz', '-SR.nii.gz')
    file_path_raw = os.path.join(root_path, file_name)
    file_path_SR = os.path.join(target_path, new_file_name)
    os.system('python predict_command_line.py {} {} --threads 1'.format(file_path_raw, file_path_SR))