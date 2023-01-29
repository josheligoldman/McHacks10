import random

import numpy as np


def dist_func(im1, im2):
    return np.linalg.norm(
        im1, im2
    )


def im_resize(im1, im2):
    height = min(im1.shape[0], im2.shape[0])
    width = min(im1.shape[1], im2.shape[1])

    return np.reshape(im1, (height, width)), np.reshape(im2, (height, width))


def calculate_im_dists(im, im_list):
    sample_ims = random.choices(im_list, k=10)

    dists = np.zeros(10, dtype=np.float64)

    for i, sample_im in enumerate(sample_ims):
        reshaped_im, reshaped_sample_im = im_resize(im, sample_im)

        dists[i] = dist_func(reshaped_im, reshaped_sample_im) / (reshaped_im.shape[0] * reshaped_im.shape[1])

    return dists









