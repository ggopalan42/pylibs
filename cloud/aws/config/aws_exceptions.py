''' This file defines several exceptions specific to the AWS functionality '''

class AWS_RegionNotImplemented(Exception):
    ''' This exception will be raised if an un-implemented region us used
        is any AWS API calls '''
    pass


class AWS_IoT_Core_ThingNameAlreadyCreated(Exception):
    ''' This exception will be raised if an thing is attempted to be created
        that has already been created '''
    pass