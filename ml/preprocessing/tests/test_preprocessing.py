''' Run various tests for testing out the preprocessing module '''

import pytest
import random
from pylibs.ml.preprocessing import train_val_utils
from pylibs.ml.preprocessing import preprocessing_exceptions


# Constants

def test_split_train_val_invalid_split_method():
    ''' Test that the function correctly raises an exception when 
        an incorrect spilt method is specified '''
    with pytest.raises(preprocessing_exceptions.MLPRE_SplitMethodNotImplemented):
        train_val_utils.split_train_val([], [], split_using='not-implemented') 

SK_SPLIT_TEST_PARAMS = {'test_size': 0.2, 'random_state': 42, 'shuffle': False}

def test_split_train_val():
    ''' Test that the split_train_val correctly splits the data '''

    # Define train and valid datasets
    train_X = random.sample(range(1,100), 80)
    train_y = random.sample(range(1,100), 80)
    val_X = random.sample(range(1,100), 20)
    val_y = random.sample(range(1,100), 20)

    print(train_X)

    # Now join them together to make full data set
    data_X = train_X + val_X
    data_y = train_y + val_y

    # Split the data using defaults. Which are sklearns train_test_split
    # with the split ration of 0.8/0.2
    ret_train_X, ret_val_X, ret_train_y, ret_val_y =      \
                   train_val_utils.split_train_val(data_X, data_y, 
                           split_using='sklearn', params=SK_SPLIT_TEST_PARAMS) 

    # Test the lengths
    assert len(ret_train_X) == 80
    assert len(ret_train_y) == 80
    assert len(ret_val_X) == 20
    assert len(ret_val_y) == 20

    # Test that split happened correctly
    assert ret_train_X == train_X
    assert ret_val_X == val_X
    assert ret_train_y == train_y
    assert ret_val_y == val_y

    print(ret_train_X)


