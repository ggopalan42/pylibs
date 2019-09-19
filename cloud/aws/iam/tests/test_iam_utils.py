''' Testing of IAM Utils '''

import pytest

from pylibs.cloud.aws.iam.iam_utils import create_role
from pylibs.cloud.aws.iam.iam_utils import list_roles
from pylibs.cloud.aws.iam.iam_utils import delete_role
from pylibs.cloud.aws.iam.iam_utils import get_role_arn


# Constants
SINGLE_ROLE_NAME = 'pytest1_single_role'
MULTI_ROLE_NAME = ['pytest1_multi_role', 'pytest2_multi_role',
                   'pytest3_multi_role']
TRUST_POLICY_JSON = {
                        "Version":"2012-10-17",
                        "Statement":[
                          {
                            "Effect":"Allow",
                            "Principal":{"Service":"lambda.amazonaws.com"},
                            "Action":"sts:AssumeRole"
                         }
                     ]}
ROLE_PATH = '/'
ROLE_DESCRIPTION = 'A test role for pytest'
ROLE_TAGS = [
           {
               'Key': 'Project',
               'Value': 'PyTest Project1'
           }
       ]

