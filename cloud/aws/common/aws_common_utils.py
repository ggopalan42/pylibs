''' This file hosts functions common to many AWS services '''

import logging
from pylibs.cloud.aws.config import aws_exceptions


def check_response_status(resp, check_failure=False):
    ''' This will check if the status code of response of a AWS IoT Core
        API call is 200 and will return True if it is and false otherwise 

        Arguments:
            - resp: Full response from AWS API calls
            - check_failure: If this flag is set, check if the call failed
                             and log and raise an error in this func itself

        Returns:
            - status_bool: True if call succedded (ie returned Status=OK
            - status_code: HTTP code of the failure
    '''
    status_code = resp['ResponseMetadata']['HTTPStatusCode']
    status_bool = True if status_code is 200 or 204 else False

    if check_failure:    # Check for failure here itself
        if not status_bool:
            logging.info(f'AWS API call to IAM get role failed with code: '
                         f'{scode}')
            raise aws_exceptions.AWS_API_CallFailed
    
    return status_bool, status_code

