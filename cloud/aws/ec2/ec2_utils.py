''' This lib contains code for working on ec2 instances '''

import boto3
import pdb

from collections import defaultdict

# Local imports
from pylibs.cloud.aws.config import aws_settings
from pylibs.cloud.aws.config import aws_exceptions


class ec2_SingleInstance():
    ''' Class that contains parameters, properties and methonds for a
        single ec2 instance '''
    def __init__(self, ec2_init_dict):
        self.aws_default_region = aws_settings.AWS_DEFAULT_REGION
        self.aws_project_name = aws_settings.AWS_PROJECT_NAME
        self._set_defaults(ec2_init_dict)
        self._start_session()

    # Private methods
    def _set_defaults(self, ec2_init_dict):
        ''' Check init_dict for keys required to start and ec2 instance
            If key is not present, initialize with defaults '''
        # These are the default params. They will not be "disturbed"
        self.ec2_default_params = {
            'InstanceType': 't3.micro',
            'MaxCount': 1,
            'MinCount': 1,
            'SecurityGroupIds':
            [aws_settings.AWS_SECURITY_GROUPS[self.aws_project_name]],
        }
        # This is the ec2_param used to create an instance. This
        # is a cmobination of ec2_default_params and ec2_init_dict
        self.ec2_params = ec2_init_dict
        self.ec2_params.update(self.ec2_default_params)

    def _start_session(self):
        ''' Start an ec2 session and store it in clss '''
        self.ec2_session = boto3.client('ec2',
                                        region_name=self.aws_default_region)

    # Public methods
    def ec2_launch_instance(self, launch_dict={}):
        ''' Launch an ec2_instance and save the session details

            Arguments:
                launch_dict: An optional dictionary that contains additional
                    parameters or updated parameters used to launch an instance
                    The parameters used for the instance launch will be
                    (a copy of) the ec2_params along with launch_dict
        '''

        # Fianlise all parameters needed to launch instance
        self.ec2_launch_params = self.ec2_params
        self.ec2_launch_params.update(launch_dict)
        print(self.ec2_launch_params)

        # Start a session
        self.ec2_response = self.ec2_session.run_instances(**self.ec2_launch_params)

        return self.ec2_response


class ec2_AllInstances():
    ''' This class holds details of all of the instances that
        have been launched '''
    def __init__(self):
        self.aws_default_region = aws_settings.AWS_DEFAULT_REGION
        self.aws_project_name = aws_settings.AWS_PROJECT_NAME
        self.ec2_sessions = defaultdict(str)   # default value of str is ''

    # Public methods
    def ec2_store_instance(self, ec2_instance):
        ''' Save the instance details in ec2_sessions dictionary

            Arguments: ec2_instance of type Class ec2SingleInstance

            Returns: None at the moment
        '''
        instance_name = ec2_instance.name
        self.ec2_sessions[instance_name] = ec2_instance


# Directly accessible methods
def get_all_instances_in_region(params_dict={},
                                region=aws_settings.AWS_DEFAULT_REGION):
    ''' Calling this function will return all running instances in the
        specified region.

        Arguments:
        ---------
            params_dict: An optional dictionary that contains parameters
                         (like instance_id, etc) on which to filter the query
                         If None, all instance data will be returned.
            region: The region on which to make the query on.
                    Note: Currently only the default region is supported
    '''

    # If a region other than default region is specified, raise an error
    if region != aws_settings.AWS_DEFAULT_REGION:
        raise aws_exceptions.AWS_RegionNotImplemented

    # Else, query the AWS region and return all found instances
    ec2_session = boto3.client('ec2',
                               region_name=aws_settings.AWS_DEFAULT_REGION)
    response = ec2_session.describe_instances()
    return response

def terminate_instances(instance_id_list):
    ec2_session = boto3.client('ec2',
                               region_name=aws_settings.AWS_DEFAULT_REGION)
    response = ec2_session.terminate_instances(InstanceIds=instance_id_list)

# Create Instance API doc:
#  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.create_instances


'''
agSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'project_name',
                    'Value': 'neutrino'
                },
            ]
        },
    ],
'''
