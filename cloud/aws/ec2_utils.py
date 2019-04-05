''' This lib contains code for working on ec2 instances '''

import boto3

from collections import defaultdict

# Local imports
from . import aws_settings


class ec2_SingleInstance():
    ''' Class that contains parameters, properties and methonds for a
        single ec2 instance '''
    def __init__(self, ec2_init_dict):
        self.aws_default_region = aws_settings.AWS_DEFAULT_REGION
        self.aws_project_name = aws_settings.AWS_PROJECT_NAME
        self._set_defaults(ec2_init_dict)

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
        self.ec2_session = boto3.client('ec2',
                                        region_name=self.aws_default_region)
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







# Create Instance API doc:  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.create_instances

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
