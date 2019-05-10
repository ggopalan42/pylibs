''' This file defines several exceptions specific to
    ML preprocessing functionality
'''


class MLPRE_SplitMethodNotImplemented(Exception):
    ''' This exception will be raised a call is made to train/val split
        function with a split method that is not implemented
        is any AWS API calls '''
    pass
