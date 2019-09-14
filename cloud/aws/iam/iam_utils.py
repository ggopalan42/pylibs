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


def create_role(role_name, trust_policy, path='/', description='',
                max_session_duration=3600, tags={}):
    ''' Create an IAM Role

        Arguments:
            - role_name: Name of the role
            - trust_policy: Trust relationship policy document (JSON string)
            - path: Path of the role. Defaults to /
            - description: Obvious
            - max_session_duration: In seconds. Default is 60 mins
            - tags: Tags in list of dict format

        Returns: A named tuple of:
           - Index 0 or role_arn: Role ARN
           - Index 1 or full_response: The full response 
                                       (minus the response meta data)
    ''' 
    # Create a named tuple
    resp_tuple = namedtuple('role_arn', 'full_response')

    # Connect to IAM
    iam_client=boto3.client('iam')

    # Create role
    resp = iam_client.create_role(
               RoleName = role_name,
               AssumeRolePolicyDocument = trust_policy,
               Path = path,
               Description = description,
               MaxSessionDuration = max_session_duration if     \
                                    max_session_duration else None,
               Tags = tags 
           )

    # Check response
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to IAM create role failed with code: '
                     f'{scode}')
        raise aws_exceptions.AWS_API_CallFailed

    return resp_tuple(esp['Role']['Arn'], resp)


def list_roles(path_prefix='/'):
    ''' List IAM Roles

        ***** Mega Note: Pagination is not being used in this version.
                         So if the number of roles is > 100, it will
                         be truncated to 100 ******
        Arguments:
            - path_prefix: The path prefix foir filtering results

        Returns:
            - roles_list: A list with role names
            - roles_dict: A dict keyed by role names with the attribute of
                          said role as values
            - resp: Full response (minus metadata)
    '''

    # Connect to IAM
    iam_client=boto3.client('iam')

    resp = iam_client.list_roles(PathPrefix = path_prefix)

    # Check response
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to IAM list roles failed with code: '
                     f'{scode}')
        raise aws_exceptions.AWS_API_CallFailed

    # Now make a distionary of roles
    roles_list_of_dicts = resp['Roles']
    roles_dict = {x['RoleName']: x for x in roles_list_of_dicts}

    roles_list = list(roles_dict.keys())

    # Delete the metata from response before returning
    del resp['ResponseMetadata']

    return roles_list, roles_dict, resp

 
 
def get_role_arn(role_name):
    ''' Get the role specified by role_name

        Arguments:
            - role_name: Name of the role
        Returns:
            - A named tuple with:
                - index 0 or role_arn: being the ARN name
                - index 1 or full_response: being the full response
    '''
    # Create a named tuple
    role_arn = namedtuple('role_arn', 'full_response')

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

    import json

    # For testing
    # resp = get_role_arn('neutrino_lambda_basic')
    # print(resp.arn)


    '''
    role_name = 'gg_test1_role'
    trust_policy_json = {
                            "Version":"2012-10-17",
                            "Statement":[
                              {
                                "Effect":"Allow",
                                "Principal":{"Service":"lambda.amazonaws.com"}, 
                                "Action":"sts:AssumeRole"
                             }
                         ]}
    trust_policy = json.dumps(trust_policy_json)
    path = '/'
    description = 'A test role for gg'
    tags = [
               {
                   'Key': 'Project',
                   'Value': 'GG Test Project1'
               }
           ] 
    arn, name, resp = create_role(role_name=role_name, 
                                  trust_policy=trust_policy, path=path, 
                                  description=description, tags=tags)
    print(arn)
    print(name)
    print(resp)
    '''
    
    roles_list, roles_dict, resp = list_roles()
    print(roles_list)
    print(roles_dict)
    print(resp)
