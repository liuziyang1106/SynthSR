""" This scripts generates 3 examples where we try to regress LR T2 scans into HR T1 scans. We assume here that HR label
maps are available with corresponding T1 scans. Thus this script produces pairs of real HR T1 scans along with aligned
HR synthetic scans, simulating LR T2 scans."""

import os
import time
import numpy as np
from ext.lab2im import utils
from SynthSR.brain_generator import BrainGenerator


# folder containing label maps to generate images from
labels_folder = '../../data/labels'
# folder containing corresponding images, that will be used as target regression
images_folder = '../../data/images/'

# result parameters
n_examples = 3  # number of generated examples
result_dir = '../../data/generated_images/3-synthesis_real'  # folder where they will be saved

# general parameters
channels = 1  # we only generate synthetic 1 channel (T2 scans).
output_channel = None  # the regression targets are not synthetic, but real
target_res = None  # produce data at the resolution of the label maps
output_shape = 128  # in this example we randomly crop the generated pairs to a shape of 128^3

# label values of structure to generate from
generation_labels = '../../data/labels_classes_priors/generation_labels.npy'
# classes associating similar structures to the same Gaussian distribution
generation_classes = '../../data/labels_classes_priors/generation_classes.npy'

# Hyperparameters governing the GMM priors for T2 scans
prior_means = '../../data/labels_classes_priors/prior_means_t2.npy'
prior_stds = '../../data/labels_classes_priors/prior_stds_t2.npy'

# augmentation parameters
# We we introduce some parameters concerning the spatial deformation. They enable to set the range of the uniform
# distribution from which the corresponding parameters are selected
flipping = True  # enable right/left flipping
scaling_bounds = 0.7  # the scaling coefficients will be sampled from U(1-scaling_bounds; 1+scaling_bounds)
rotation_bounds = 8  # the rotation angles will be sampled from U(-rotation_bounds; rotation_bounds)
shearing_bounds = 0.01  # the shearing coefficients will be sampled from U(-shearing_bounds; shearing_bounds)
translation_bounds = False  # no translation is performed, as this is already modelled by the random cropping
nonlin_std = 2.  # this controls the maximum elastic deformation (higher = more deformation)
bias_field_std = 0.2  # his controls the maximum bias field corruption (higher = more bias)

# blurring/downsampling parameters
data_res = np.array([1., 4.5, 1.])  # slice spacing
thickness = np.array([1., 3., 1.])  # slice thickness
downsample = True  # downsample to simulated LR
build_reliability_maps = True  # add reliability map to input channels


########################################################################################################

# instantiate BrainGenerator object
brain_generator = BrainGenerator(labels_dir=labels_folder,
                                 images_dir=images_folder,
                                 generation_labels=generation_labels,
                                 n_channels=channels,
                                 output_channel=output_channel,
                                 target_res=target_res,
                                 output_shape=output_shape,
                                 generation_classes=generation_classes,
                                 prior_means=prior_means,
                                 prior_stds=prior_stds,
                                 flipping=flipping,
                                 scaling_bounds=scaling_bounds,
                                 rotation_bounds=rotation_bounds,
                                 shearing_bounds=shearing_bounds,
                                 translation_bounds=translation_bounds,
                                 nonlin_std=nonlin_std,
                                 bias_field_std=bias_field_std,
                                 data_res=data_res,
                                 thickness=thickness,
                                 downsample=downsample,
                                 build_reliability_maps=build_reliability_maps)

# create result dir
utils.mkdir(result_dir)

for n in range(n_examples):

    # generate !
    start = time.time()
    input_channels, regression_target = brain_generator.generate_brain()
    end = time.time()
    print('generation {0:d} took {1:.01f}s'.format(n+1, end - start))

    # save output image and label map
    utils.save_volume(np.squeeze(input_channels[..., 0]), brain_generator.aff, brain_generator.header,
                      os.path.join(result_dir, 't1_input_%s.nii.gz' % n))
    utils.save_volume(np.squeeze(input_channels[..., 1]), brain_generator.aff, brain_generator.header,
                      os.path.join(result_dir, 'reliability_map_input_%s.nii.gz' % n))
    utils.save_volume(np.squeeze(regression_target), brain_generator.aff, brain_generator.header,
                      os.path.join(result_dir, 't1_target_%s.nii.gz' % n))
