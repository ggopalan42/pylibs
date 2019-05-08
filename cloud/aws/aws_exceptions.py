''' This file defines several exceptions specific to the AWS functionality '''

class AWS_RegionNotImplemented(Exception):
    ''' This exception will be raised if an un-implemented region us used
        is any AWS API calls '''
    pass
