# python imports
import numpy as np
import numpy.random as npr

# third-party imports
from ext.lab2im import utils


def build_model_inputs(path_label_maps,
                       n_labels,
                       prior_means,
                       prior_stds,
                       prior_distributions,
                       path_images=None,
                       batchsize=1,
                       n_channels=1,
                       generation_classes=None):
    """
    This function builds a generator to be fed to the lab2im model. It enables to generate all the required inputs,
    according to the operations performed in the model.
    :param path_label_maps: list of the paths of the input label maps.
    :param n_labels: number of labels in the input label maps.
    :param prior_distributions: (optional) type of distribution from which we sample the GMM parameters.
    Can either be 'uniform', or 'normal'. Default is 'uniform'.
    :param prior_means: (optional) hyperparameters controlling the prior distributions of the GMM means. Because
    these prior distributions are uniform or normal, they require by 2 hyperparameters. Thus prior_means can be:
    1) a sequence of length 2, directly defining the two hyperparameters: [min, max] if prior_distributions is
    uniform, [mean, std] if the distribution is normal. The GMM means of are independently sampled at each
    mini_batch from the same distribution.
    2) an array of shape (2, K), where K is the number of classes (K=len(generation_labels) if generation_classes is
    not given). The mean of the Gaussian distribution associated to class k in [0, ...K-1] is sampled at each mini-batch
    from U(prior_means[0,k], prior_means[1,k]) if prior_distributions is uniform, or from
    N(prior_means[0,k], prior_means[1,k]) if prior_distributions is normal.
    3) an array of shape (2*n_mod, K), where each block of two rows is associated to hyperparameters derived
    from different modalities. In this case, if use_specific_stats_for_channel is False, we first randomly select a
    modality from the n_mod possibilities, and we sample the GMM means like in 2).
    If use_specific_stats_for_channel is True, each block of two rows correspond to a different channel
    (n_mod=n_channels), thus we select the corresponding block to each channel rather than randomly drawing it.
    4) the path to such a numpy array.
    Default is None, which corresponds to prior_means = [25, 225].
    :param prior_stds: (optional) same as prior_means but for the standard deviations of the GMM.
    Default is None, which corresponds to prior_stds = [5, 25].
    :param path_images: optionally, corresponding image intensities (useful for regression)
    :param batchsize: (optional) numbers of images to generate per mini-batch. Default is 1.
    :param n_channels: (optional) number of channels to be synthetised. Default is 1.
    :param generation_classes: (optional) Indices regrouping generation labels into classes of same intensity
    distribution. Regouped labels will thus share the same Gaussian when samling a new image. Can be a sequence or a
    1d numpy array. It should have the same length as generation_labels, and contain values between 0 and K-1, where K
    is the total number of classes. Default is all labels have different classes.
    """

    # get label info
    _, _, n_dims, _, _, _ = utils.get_volume_info(path_label_maps[0])

    # allocate unique class to each label if generation classes is not given
    if generation_classes is None:
        generation_classes = np.arange(n_labels)

    # Generate!
    while True:

        # randomly pick as many images as batchsize
        indices = npr.randint(len(path_label_maps), size=batchsize)

        # initialise input lists
        list_label_maps = []
        list_means = []
        list_stds = []
        list_images = []

        for idx in indices:

            # add labels to inputs
            lab = utils.load_volume(path_label_maps[idx], dtype='int', aff_ref=np.eye(4))
            list_label_maps.append(utils.add_axis(lab, axis=[0, -1]))

            if path_images is not None:
                im = utils.load_volume(path_images[idx], dtype='float')
                list_images.append(im[np.newaxis, :, :, :, np.newaxis])

            # add means and standard deviations to inputs
            means = np.empty((1, n_labels, 0))
            stds = np.empty((1, n_labels, 0))
            for channel in range(n_channels):

                # retrieve channel specific stats if necessary
                if isinstance(prior_means, np.ndarray):
                    if prior_means.shape[0] / 2 != n_channels:
                        raise ValueError("the number of blocks in prior_means does not match n_channels.")
                    tmp_prior_means = prior_means[2 * channel:2 * channel + 2, :]
                else:
                    tmp_prior_means = prior_means
                if isinstance(prior_stds, np.ndarray):
                    if prior_stds.shape[0] / 2 != n_channels:
                        raise ValueError("the number of blocks in prior_stds does not match n_channels.")
                    tmp_prior_stds = prior_stds[2 * channel:2 * channel + 2, :]
                else:
                    tmp_prior_stds = prior_stds

                # draw means and std devs from priors
                tmp_classes_means = utils.draw_value_from_distribution(tmp_prior_means, n_labels, prior_distributions,
                                                                       125., 100., positive_only=True)
                tmp_classes_stds = utils.draw_value_from_distribution(tmp_prior_stds, n_labels, prior_distributions,
                                                                      15., 10., positive_only=True)
                tmp_means = utils.add_axis(tmp_classes_means[generation_classes], axis=[0, -1])
                tmp_stds = utils.add_axis(tmp_classes_stds[generation_classes], axis=[0, -1])
                means = np.concatenate([means, tmp_means], axis=-1)
                stds = np.concatenate([stds, tmp_stds], axis=-1)
            list_means.append(means)
            list_stds.append(stds)

        # build list of inputs for generation model
        list_inputs = [list_label_maps, list_means, list_stds]
        if path_images is not None:
            list_inputs.append(list_images)


        if batchsize > 1:  # concatenate each input type if batchsize > 1
            list_inputs = [np.concatenate(item, 0) for item in list_inputs]
        else:
            list_inputs = [item[0] for item in list_inputs]

        yield list_inputs
