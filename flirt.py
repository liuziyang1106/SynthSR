import os

root_path = './C3-T1-Raw'
target_path = './C3-T1-lin-spline'
for files in os.listdir(root_path):
    files_path = os.path.join(root_path, files)
    target_file = os.path.join(target_path, files.replace('.nii.gz','_sinc.nii.gz'))
    print(files_path, target_file)
    os.system('flirt -in {} -ref /usr/share/fsl/5.0/data/standard/MNI152_T1_2mm.nii.gz -dof 12 -cost normmi -out {} -interp spline'.format(
               files_path, target_file
    ))