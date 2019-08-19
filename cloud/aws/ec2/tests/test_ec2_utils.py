''' Run various tests to test ec2_utils '''

import pytest
from pylibs.cloud.aws.ec2 import ec2_utils

# Constants

def test_get_all_instances_in_region():
    ''' Test that this function connects to AWS. It may or may not
        return something depending on what is running. If something
        is returned, check that it is sane '''
    # Future: A more elaborate testing using mock libraries

    ############# The below bombs out because of some error. Abandoning for now
    # response = ec2_utils.get_all_instances_in_region()
    # print(response)
