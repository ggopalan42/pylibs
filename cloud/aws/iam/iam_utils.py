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
logging.basicConfig(level=logging.INFO)


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
        logging.info(f'IAM: Creating Role: {role_name}')
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


def create_policy(policy_name, policy_document, path='/', description=''):
    ''' Create a policy named: policy_name with the specification
        in: policy_document 

        Arguments:
            - policy_name: Name of the policy to create. A string
            - policy_document: A JSON string that specified the policy.
                               See below (or in tests) for an example
            - path: The path where policy resides. can be any valid path.
            - description: Description of the policy. A string

        Returns:
            - policy_arn: The ARN of the created policy. Null if failed
            - full_response: The full response to the API call (minus metadata)
    '''

    # Connect to IAM
    iam_client=boto3.client('iam')

    try:
        # Now create the policy
        logging.info(f'Creating policy named {policy_name}')
        resp = iam_client.create_policy(PolicyName=policy_name, 
                                        PolicyDocument=policy_document, 
                                        Path=path, Description=description) 
        aws_common_utils.check_response_status(resp, check_failure=True)

    except iam_client.exceptions.EntityAlreadyExistsException:
        logging.error(f'IAM: Create Policy: {policy_name} already exists')
        # Construct response
        err_code = aws_error_codes.AWS_IAM_POLICY_ALREADY_EXISTS
        resp = aws_error_codes.construct_response(err_code) 
        return False, resp
                   
    # Return the created policy ARN and the full response
    return resp['Policy']['Arn'], resp


def delete_policy(policy_name):
    ''' Delete the policy specified by policy_name

        Note 1: Policy must be detached and all versions deleted before
                the policy can be deleted
        Note 2: Need to provide the policy arn here. You can get policy
                arn from get_policy_arn call 
    '''

    # Get policy arn from policy name
    policy_arn = get_policy_arn(policy_name)
    # If policy name does not exist, return error
    if not policy_arn:
        logging.error(f'IAM: Delete Policy: {policy_name} does not exist')
        # Construct response
        err_code = aws_error_codes.AWS_IAM_POLICY_DOES_NOT_EXIST
        resp = aws_error_codes.construct_response(err_code)
        return False, resp

    # Connect to IAM
    iam_client=boto3.client('iam')

    try:
        logging.info(f'Deleting policy ARN: {policy_arn}')
        resp = iam_client.delete_policy(PolicyArn=policy_arn)
        aws_common_utils.check_response_status(resp, check_failure=True)
    except iam_client.exceptions.NoSuchEntityException:
        logging.error(f'IAM: Delete Policy: {policy_arn} does not exist')
        # Construct response
        err_code = aws_error_codes.AWS_IAM_POLICY_DOES_NOT_EXIST
        resp = aws_error_codes.construct_response(err_code) 
        return False, resp

    # If above call does not raise an exception, then call has succeded
    # return OK

    return True, {}
    

def list_policies(policy_scope='Local', only_attached=True, path_prefix='/',
                  policy_usage_filter='PermissionsPolicy'):
    ''' Return a list of policies

      Arguments:
        - policy_scope: Choices are:
                           All: All policies
                           AWS: All AWS managed policies
                           Local: All customer managed policies (default)
        - only_attached: If True, return only attached policies. If False
                         return all policies (True is default)
        - path_prefix: The path prefix for filtering the results. Default is '/'
        - policy_usage_filter: Choices are:
                  - PermissionsPolicy: Filter only permissions policy (default) 
                  - PermissionsBoundary: Filter only policies set for
                                         permissions boundary

      Returns:
          - policy_names: A list of policy names
          - policy_arns: A list of dicts with ploicy_name: policy_arn
          - full_response: Full response of the API call
    
    #### Note: Pagination is not being used for results. As such, this
               call can handle only upto 100 policies
    '''
    # Connect to IAM
    iam_client=boto3.client('iam')

    # Call List policies API
    logging.info('Getting list of policies from AWS')
    resp = iam_client.list_policies(Scope=policy_scope, 
                                    OnlyAttached=only_attached,
                                    PathPrefix=path_prefix,
                                    PolicyUsageFilter=policy_usage_filter)
    aws_common_utils.check_response_status(resp, check_failure=True)
    
    if resp['IsTruncated']:
        logging.error('List policies returned truncated response. '
                      'Returning all policies that were returned '
                      'Time to switch to pagination . . . ')

    # Get full list of policies
    policies_list_full = resp['Policies']
    # Then get other needed items
    policies_names_list = [x['PolicyName'] for x in policies_list_full]
    # Do a dict comprehension to return policy_name: policy_arn
    policies_name_arn_dict = {x['PolicyName']: x['Arn'] for x in 
                              policies_list_full}

    return policies_names_list, policies_name_arn_dict, resp

def get_policy_arn(policy_name):
    ''' From policy name, get and retiurn the policy ARN '''

    # First get all of the policies
    policies_list, policies_arn_dict, _ =     \
                  list_policies(policy_scope='All', only_attached=False,
                                path_prefix='/',
                                policy_usage_filter='PermissionsPolicy') 

    # Check if policy name in the policies_list
    if policy_name in policies_list:
        # Return the ARN
        return policies_arn_dict[policy_name]
    # If name has not been found, then get a list with policy_usage_filter
    # set to PermissionsBoundary
    else:
        policies_list, policies_arn_dict, _ =     \
                  list_policies(policy_scope='All', only_attached=False,
                                path_prefix='/',
                                policy_usage_filter='PermissionsBoundary') 
        # Check again
        if policy_name in policies_list:
            # Return the ARN
            return policies_arn_dict[policy_name]
        else:
            return False
    

def make_managed_policy_arn(managed_policy_name):
    ''' Given a managed policy name, make a policy arn

        Note: This function is needed since boto3 API call for
              list policies does not apper to return managed policies

        - Arguments:
            - managed_policy_name: Obvious

        - Returns:
            - mamanged_policy_arn: Obvious
    '''

    return f'arn:aws:iam::aws:policy/{managed_policy_name}'


def attach_managed_policy_to_role(role_name, policy_name):
    ''' Attach a managed policy to a role

        Arguments:
            - role_name: Role name to attach policy to (name, not ARN)
            - policy_name: Managed policy name to attach to policy (not ARN)

        Returns: True if successful
    '''
    managed_policy_arn = make_managed_policy_arn(policy_name)

    # Connect to IAM
    iam_client=boto3.client('iam')

    # Attach the policy to the role
    logging.info(f'Attaching policy: {policy_name} to role: {role_name}')
    resp = iam_client.attach_role_policy(RoleName=role_name, 
                                         PolicyArn=managed_policy_arn)
    aws_common_utils.check_response_status(resp, check_failure=True)

    # If it falls through, then return success
    return True, {}


def detach_managed_policy_from_role(role_name, policy_name):
    ''' Detach a managed policy from a role

        Arguments:
            - role_name: Role name to attach policy to (name, not ARN)
            - policy_name: Managed policy name to attach to policy (not ARN)

        Returns: True if successful

         Note: Sometime if the attach fails (like role does not exist)
               a botocore exception is raised. A future improvement
               will be to catch this and return an error code
    '''
    managed_policy_arn = make_managed_policy_arn(policy_name)

    # Connect to IAM
    iam_client=boto3.client('iam')

    # Detach the policy from the role
    logging.info(f'Detaching policy: {policy_name} from role: {role_name}')
    resp = iam_client.detach_role_policy(RoleName=role_name,
                                         PolicyArn=managed_policy_arn)
    aws_common_utils.check_response_status(resp, check_failure=True)

    # If it falls through, then return success
    return True, {}


def attach_inline_policy_to_role(role_name, policy_name, policy_document):
    ''' Attach an inline policy to the role

        Arguments:
            - role_name: name of role, a string (not ARN)
            - policy_name: name of policy, a string (not ARN)
            - policy_document: A JSON of the ploic document.
                               See below (or in tests) for example
       Return:
           - True if attach succeds

             Note: Sometime if the attach fails (like role does not exist)
                   a botocore exception is raised. A future improvement
                   will be to catch this and return an error code
    '''

    # Connect to IAM
    iam_client=boto3.client('iam')

    logging.info(f'Attaching inline policy: {policy_name} to role: {role_name}')

    resp = iam_client.put_role_policy(RoleName=role_name,
                                      PolicyName=policy_name,
                                      PolicyDocument=policy_document)

    aws_common_utils.check_response_status(resp, check_failure=True)

    # If it falls through, then return success
    return True, {}


def detach_inline_policy_to_role(role_name, policy_name):
    ''' Detach an inline policy '''
    # Note: Cant figure out how to do this from the boto3 docs.
    #       Leaving it as not implemented as of now
    logging.error('Detach inline policy from role not implemented')
    raise aws_exceptions.AWS_NotImplementedError


if __name__ == '__main__':

    import json

    # For testing
    # resp = get_role_arn('neutrino_lambda_basic')
    # print(resp.arn)


    ############## Define a test role ######################
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
    trust_policy_path = '/'
    trust_policy_description = 'A test role for gg'
    trust_policy_tags = [
               {
                   'Key': 'Project',
                   'Value': 'GG Test Project1'
               }
           ] 

    ############## Define a test policy ######################
    policy_name = 'gg_test1_policy'
    policy_doc_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:GetItem",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": "arn:aws:dynamodb:us-west-2:272566984931:table/gg_test1"
                }
            ]
        }
    policy_doc = json.dumps(policy_doc_json)
    policy_path = '/'
    policy_description = 'Dyn db allow policy'


    '''
    ############## Create Role ######################
    arn, resp = create_role(role_name=role_name, 
                                  trust_policy=trust_policy, 
                                  path=trust_policy_path, 
                                  description=trust_policy_description, 
                                  tags=trust_policy_tags)
    print(arn)
    print(resp)
    '''
    
    '''
    ############## List Roles ######################
    roles_list, roles_dict, resp = list_roles()
    print(roles_list)
    # print(roles_dict)
    # print(resp)

    ############## Delete Role ######################
    resp_code, resp = delete_role(role_name)
    print(resp_code)
    '''

    '''
    ############## Create Policy ######################
    policy_arn, full_resp  = create_policy(policy_name, policy_doc, 
                                           path=policy_path, 
                                           description=policy_description)
    print(policy_arn)
    print()
    print(full_resp)
    '''

    '''
    ############## List Policy ######################
    policies_list, policies_arn_list, full_response  = list_policies(only_attached=False)
    print(policies_list)
    print(policies_arn_list)
    '''

    '''
    ############## Get Policy ARN ######################
    arn = get_policy_arn('AmazonDynamoDBFullAccess') 
    print(arn)
    '''

    '''
    ############## Delete Policy ######################
    resp = delete_policy('gg_test2_policy')
    print(resp)
    '''

    '''
    ############## Attach managed Policy ######################
    resp = attach_managed_policy_to_role('gg_test1_role', 
                                               'AmazonDynamoDBFullAccess')
    print(resp)
    '''

    '''
    ############## Detach managed Policy ######################
    resp = detach_managed_policy_from_role('gg_test1_role', 
                                               'AmazonDynamoDBFullAccess')
    print(resp)
    '''

    '''
    ############## Attach Inline Policy ######################
    resp = attach_inline_policy_to_role(role_name, policy_name, policy_doc)
    print(resp)
    '''

    '''
    ############## Detach Inline Policy ######################
    resp = detach_inline_policy_to_role(role_name, policy_name)
    print(resp)
    '''
