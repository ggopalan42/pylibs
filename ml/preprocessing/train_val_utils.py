''' Provides utilities relevant to Machine Learning tasks. These include:
    - split_train_val:  Given a list of train data and labels, split
                        them into train and val lists providing decent defaults
'''

import os
import random

from . import preprocessing_exceptions

# ML related imports
from sklearn.model_selection import train_test_split

# Constants
SK_SPLIT_DEF_PARAMS = {'test_size': 0.2, 'random_state': 42, 'shuffle': True}
def split_train_val(data_X, data_y, split_using='sklearn',
                    params=SK_SPLIT_DEF_PARAMS):
    ''' Split the provided labelled data to train and validation data

    Args:
        data_X: List of data in pretty much and dtype
        data_y: List of labels for the data
        split_using: This specifies the method used to split the data.
                     Currently supported method are:
                         - sklearn: Use standard sci-kit learn's
                                    train_test_split
        params: Parametes for the chosen split method provided as a dict
    Returns:
        Tuple of (train_X, val_X, train_y, val_y): The return parameters are
                                                   self explanatory
    '''
    if split_using == 'sklearn':
        test_size = params['test_size']
        random_state = params['random_state']
        shuffle = params['shuffle']
        return train_test_split(data_X, data_y,
                                test_size=test_size, random_state=random_state,
                                shuffle=shuffle)
    else:
        msg = f'Unsupported split method: {split_using}'
        raise preprocessing_exceptions.MLPRE_SplitMethodNotImplemented(msg)


if __name__ == '__main__':
    # This is purely for testing purposes. Not unit testing, mind you
    data_X = random.sample(range(1,10), 9)
    data_y = random.sample(range(1,10), 9)
    train_X, val_X, train_y, val_y = split_train_val(data_X, data_y,
                                                     split_using='sklearn')
    print(train_X)
    print(train_y)
    print(val_X)
    print(val_y)
