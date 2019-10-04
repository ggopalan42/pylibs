''' This defines a bunch of functions that are useful for using AWS Lambda '''

import os
import boto3
import logging

# Local imports
from pylibs.cloud.aws.config import aws_settings
from pylibs.cloud.aws.config import aws_error_codes
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

        Returns:
           - role_arn: Role ARN
           - full_response: The full response (minus the response meta data)
    ''' 
    # Connect to IAM
    iam_client=boto3.client('iam')

    # Create role
    try:
        resp = iam_client.create_role(
                   RoleName = role_name,
                   AssumeRolePolicyDocument = trust_policy,
                   Path = path,
                   Description = description,
                   MaxSessionDuration = max_session_duration if     \
                                        max_session_duration else None,
                   Tags = tags 
               )
    except iam_client.exceptions.EntityAlreadyExistsException:
        logging.error(f'IAM: Create Role: {role_name} already exists')
        # Construct response
        err_code = aws_error_codes.AWS_IAM_ROLE_ALREADY_EXISTS
        resp = aws_error_codes.construct_response(err_code) 
        return False, resp
                   

    # Check response
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to IAM create role failed with code: '
                     f'{scode}')
        raise aws_exceptions.AWS_API_CallFailed

    return resp['Role']['Arn'], resp


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


def delete_role(role_name):
    ''' Delete Role

        Arguments:
            - role_name: Role name to be deleted

        Returns:
            - resp: Full response (minus metadata)
    '''

    # Connect to IAM
    iam_client=boto3.client('iam')

    try:
        resp = iam_client.delete_role(RoleName = role_name)
    except iam_client.exceptions.NoSuchEntityException:
        logging.error(f'IAM: Delete Role: {role_name} does not exist')
        # Construct response
        err_code = aws_error_codes.AWS_IAM_ROLE_DOES_NOT_EXIST
        resp = aws_error_codes.construct_response(err_code)
        return False, resp

    # Check response
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to IAM delete roles failed with code: '
                     f'{scode}')
        raise aws_exceptions.AWS_API_CallFailed

    err_code = aws_error_codes.AWS_NO_ERROR
    resp = aws_error_codes.construct_response(err_code)
    return True, resp
 
 
def get_role_arn(role_name):
    ''' Get the role specified by role_name

        Arguments:
            - role_name: Name of the role
        Returns:
            - role_arn: being the ARN name
            - full_response: being the full response
    '''
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
    return resp['Role']['Arn'], resp

if __name__ == '__main__':

    import json

    # For testing
    # resp = get_role_arn('neutrino_lambda_basic')
    # print(resp.arn)


    role_name = 'gg_test2_role'
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
    '''
    arn, resp = create_role(role_name=role_name, 
                                  trust_policy=trust_policy, path=path, 
                                  description=description, tags=tags)
    print(arn)
    print(resp)
    '''
    
    roles_list, roles_dict, resp = list_roles()
    print(roles_list)
    # print(roles_dict)
    # print(resp)

    resp_code, resp = delete_role(role_name)
    print(resp_code)
    print(resp)
