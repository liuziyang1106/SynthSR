#!/bin/bash
# this script is to perform preprocess of T1 images:
# include linear reg, non linear reg and brain extraction

## directory
ROOTDIR=../C3-T1-tsan-prep/
cd ${ROOTDIR}
files=(ls *.nii.gz)
pip (){
    local sta=$1
    local num=$2
    echo "process $sta : $((sta+num))"
    
    #loop
    for file in ${files[@]:$sta:$num};do
        
        # new folder
        data_folder=${file::8}
        mkdir $data_folder
        mv $file $data_folder
        cd $data_folder

        # pre-process
        fsl_anat_tsan -i $file
        echo "done pre-processing"
        echo

        # ori folder
        cd ..
    done
}

# Example:
# Suppose we have 3000 cases of MRI images that need to be preprocessed, 
# and we want to use 10 threads in the server for parallel processing, 
# so that each thread will allocate 300 cases of data for processing 

# When calling the pip function, 
# you only need to set the starting index number of the preprocessed data and 
# the number of data to be processed by the thread 
pip 1  10 &
pip 11 10 &
pip 21 10 &
pip 31 10 &
pip 41 10 &


