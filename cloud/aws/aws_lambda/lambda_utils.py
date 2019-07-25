''' This defines a bunch of functions that are useful for using AWS Lambda '''

import os
import boto3
import logging

from botocore.exceptions import ClientError

from pylibs.cloud.aws.config import aws_settings
from pylibs.cloud.aws.config import aws_exceptions
from pylibs.cloud.aws.common import aws_common_utils

# Constants

# Set logging level
# logging.basicConfig(level=logging.INFO)


 
def list_functions(aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' List all functions in requested region

        Arguments:
            - aws_region: List buckets in this region. 'ALL' can also be used
        Returns:
            - A tuple with:
                - index 0 being a list of function named
                - index 1 being a list of the entire response
    '''
    func_name_list = []
    func_full_list = []
    lambda_client = boto3.client('lambda')

    # pagination is used in case there are > 1000 functions
    paginator = lambda_client.get_paginator('list_functions')
    # For some reason, specifying MasterRegion is paginate call returns no 
    # functions. Debug later
    # pages = paginator.paginate(MasterRegion=aws_region, FunctionVersion='ALL')
    pages = paginator.paginate()

    for page in pages:
        # Check if call succeded
        sbool, scode = aws_common_utils.check_response_status(page)
        if not sbool:
            logging.info(f'AWS API call to list lambda functions failed with '
                         f'code: {scode}')
            raise aws_exceptions.AWS_API_CallFailed
        for func in page['Functions']:
            func_name_list.append(func['FunctionName'])
            func_full_list.append(func)
    return func_name_list, func_full_list
   
def get_function(func_name):
    ''' Get information about func_name

        Arguments:
            - func_name: Name of the function for which information is requested
        Returns: A dict with keys:
             - Configuration: Which has info line func ARN, runtime, mem size
             - Code: The (zipped) function code. 
                     I beleive this is valid for 10 min
             - Tags: Tags for the function
    '''
    lambda_client = boto3.client('lambda')
    resp = lambda_client.get_function(FunctionName=func_name)
    # Check for the response
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to list lambda functions failed with '
                     f'code: {scode}')
        raise aws_exceptions.AWS_API_CallFailed

    # If call succeded, simply delete the 'ResponseMetadata' key from the
    # response dict and return the remaining
    del(resp['ResponseMetadata'])
    return(resp)
    

if __name__ == '__main__':

    # For testing
    '''
    resp = list_functions()
    print(resp[1])
    '''
    resp = get_function('gg_iot_core_labmda_01')
    print(resp)
