''' This defines a bunch of functions that are useful for using AWS Lambda '''

import os
import boto3
import logging

from collections import namedtuple
from botocore.exceptions import ClientError

# Local imports
from pylibs.cloud.aws.config import aws_settings
from pylibs.cloud.aws.config import aws_exceptions
from pylibs.cloud.aws.common import aws_common_utils

# Constants

# Set logging level
# logging.basicConfig(level=logging.INFO)


 
def get_role_arn(role_name):
    ''' Get the role specified by role_name

        Arguments:
            - role_name: Name of the role
        Returns:
            - A named tuple with:
                - index 0 or arn: being the ARN name
                - index 1 or full_response: being the full response
    '''
    # Create a named tuple
    role_arn = namedtuple('role_arn', 'arn full_response')

    # Connect to IAM and query the role
    iam_client=boto3.client('iam')
    resp = iam_client.get_role(RoleName=role_name) 

    # Check if request worked
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to IAM get role failed with code: '
                     f'{scode}')
        raise aws_exceptions.AWS_API_CallFailed

    # Split up and return the response
    return role_arn(resp['Role']['Arn'], resp)

if __name__ == '__main__':

    # For testing

    resp = get_role_arn('neutrino_lambda_basic')
    print(resp.arn)
