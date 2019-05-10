''' Provides utilities relevant to Machine Learning tasks. These include:
    - split_train_val:  Given a list of train data and labels, split
                        them into train and val lists providing decent defaults
'''

import os

import preprocessing_exceptions


SK_SPLIT_DEF_PARAMS = {'test_size': 0.2, 'random_state': 42}
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
        Tuple of (train_X, train_y, val_X, val_y): The return parameters are
                                                   self explanatory
    '''
    if split_using not in ['sklearn']:
        msg = f'unsupported split method: {split_using}'
        raise preprocessing_exceptions.MLPRE_SplitMethodNotImplemented(msg)

if __name__ == '__main__':
    # This is purely for testing purposes. Not unit testing, mind you
    split_train_val([], [], split_using='dim')
