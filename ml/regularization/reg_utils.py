''' List of useful regularization routines '''

import numpy as np

def l2_normalize(x, axis=-1, epsilon=1e-10):
    output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, 
                         keepdims=True), epsilon))
    return output

