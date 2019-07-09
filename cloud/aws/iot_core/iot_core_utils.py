''' This defines a bunch of functions that are useful for using the AWS
    IoT Core functionality 

    The general steps for creating a IoT "thing" as AWS calls it are:
        1. Create a thing and register it in the registry
            a. Create and activate a device cert
            b. Create an AWS IoT policy
            c. Attach AWS policy to the cert
            d. Attach cert to a thing

'''

import sys
import os
import boto3
import time
import pickle

from pylibs.cloud.aws.config import aws_iot_core_settings

# Constant
# this stuff needs to be made better. Store in a better location/name
PICKLE_STORE_NAME = os.path.join(os.path.expanduser('~'), 'all_things.pkl') 

# Below like is liky bit.ly. Make the big, descriptive name small
default_thing_policy_name =       \
                     aws_iot_core_settings.IOT_CORE_DEFAULT_THING_POLICY_NAME

class aws_iot_thing():
    ''' This object holds all data and methods that represent a single
        AWS IoT thing '''
    def __init__(self):
        # Init connection to AWS
        self.iot_client = boto3.client('iot')

    def create_thing(self, thing_name, thing_type_name, 
                     attributes={}, billing_group_name=None):
        ''' Create an AWS IoT thing

          Arguments:
            thing_name = Name of the IoT thing
            thing_type_name = Name of the (already created) thing type
            attributes = Attributes for the thing. Provided as a dict
            billing_group_name = Provide this if thing needs to be associated
                                 with a billing group

          Response: Response from the API call to AWS IoT
        '''
        # Create iot thing
        if billing_group_name:
            r= self.iot_client.create_thing(thingName=thing_name, 
                                            thingTypeName=thing_type_name, 
                                            attributePayload=attributes,
                                            billingGroupName=billing_group_name)
        else:
            r= self.iot_client.create_thing(thingName=thing_name, 
                                            thingTypeName=thing_type_name, 
                                            attributePayload=attributes)
        # Record the response
        self.creation_response = r
        return(r)


    def delete_thing(self, thing_name):
        ''' Delete an AWS IoT thing

          Arguments:
            thing_name = Name of the IoT thing to be deleted
        '''
        resp = self.iot_client.delete_thing(thingName=thing_name)
        return resp




class aws_iot_all_things():
    ''' This object holds the data for all AWS IoT things
        AWS IoT thing '''
    def __init__(self):
        self.iot_things_list = []     # This is simply a list of names
        self.iot_things_objs = {}     # This is a dict of names and its
                                      # aws_iot_thing class

    def create_thing(self, thing_name, thing_type_name,
                     attributes={}, billing_group_name=None):

        ''' Create an AWS IoT thing type and record it. This will simply call
            the create_thing method of class aws_iot_thing but record
            all of the details

          Arguments:
            thing_name = Name of the IoT thing
            thing_type_name = Name of the (already created) thing type
            attributes = Attributes for the thing. Provided as a dict
            billing_group_name = Provide this if thing needs to be associated
                                 with a billing group

          Response: Response from the API call to AWS IoT
        '''

        # Instantiate
        iot_thing_obj = aws_iot_thing()
        # Create
        resp = iot_thing_obj.create_thing(thing_name, thing_type_name, 
                                          attributes, billing_group_name)
        # Record
        self.iot_things_list.append(thing_name)
        self.iot_things_objs[thing_name] = iot_thing_obj

        return resp 


    def delete_thing(self, thing_name):

        ''' Delete the specified AWS IoT thing and remove it from the records.
            This will simply call the delete_thing

          Arguments:
            thing_name = Name of the IoT thing
        '''
        # First call the delete thing method of the thing_name's class obj
        resp = self.iot_things_objs[thing_name].delete_thing(thing_name)
        # Then remove records
        self.iot_things_list.remove(thing_name)
        del self.iot_things_objs[thing_name]
        return resp


    def list_all_things(self):
        ''' Get and return a list of AWS IoT things

          Arguments: None

          Returns:
              - A list of thing names
              - The full API call response 
        '''
        # Create a connection
        client = boto3.client('iot')
        # Get the full response to list things
        # Get the list of thing types
        response_full = client.list_things()

        # Extract just the thing names
        # The response is a dict that has two keys: 
        # 'ResponseMetadata' and 'things'. And 'things' is a list
        # of dicts with key 'thingName' which is where we get all
        # of the thing names
        thing_names = []
        for thing in response_full['things']:
            thing_names.append(thing['thingName'])
        return thing_names, response_full


class aws_iot_thing_type():
    ''' This object holds all data and methods that represent
        an AWS IoT thing type '''
    def __init__(self):
        # Init connection to AWS
        self.iot_client = boto3.client('iot')

    def create_thing_type(self, thing_type_name, properties={}, tags=[]):
        ''' Method for creating iot thing type 

          Arguments:
            thing_type_name: name of the type to be created
            properties: dict of properties to be set. 
                        Things like description and searchable string
            tags: List of tage for this thing type
        '''

        # Create thing type
        response = self.iot_client.create_thing_type(thingTypeName=
                                                     thing_type_name,
                                     thingTypeProperties=properties, tags=tags)
        return response


    def deprecate_thing_type(self, thing_type_name):
        ''' Method for deprecating iot thing type 

          Arguments:
            thing_type_name: name of the type to be deprecated
        '''
        # Deprecate the thing
        response = self.iot_client.deprecate_thing_type(thingTypeName=
                                                        thing_type_name,
                                                        undoDeprecate=False)
        return response


    def delete_thing_type(self, thing_type_name):
        ''' Method for deleting iot thing type 

          Arguments:
            thing_type_name: name of the type to be deleted
        '''
        # Delete the thing type
        response = self.iot_client.delete_thing_type(thingTypeName=
                                                     thing_type_name)
        return response


    def list_all_thing_types(self):
        ''' Method for listing all thing types

          Arguments: None
        '''
        # Get the list of thing types
        response_full = self.iot_client.list_thing_types()

        # Extract just the thing type names
        # The response is a dict that has two keys: 
        # 'ResponseMetadata' and 'thingTypes'. And 'thingTypes' is a list
        # of dicts with key 'thingTypeName' which is where we get all
        # of the thing type names
        tt_names = []
        for tt in response_full['thingTypes']:
            tt_names.append(tt['thingTypeName'])
        return tt_names, response_full


    def get_thing_type_properties(self, thing_type_name):
        ''' Get all of the associated data for 'thing_type_name'

          Arguments:
              thing_type_name: The name of the thing type for which data
                               is needed
        '''
        # get the data for the specified thing_type_name and return the
        # response as is
        response = self.iot_client.list_thing_types(thingTypeName=
                                                    thing_type_name)
        return response['thingTypes']

def check_response_status(resp):
    ''' This will check if the status code of response of a AWS IoT Core
        API call is 200 and will return True if it is and false otherwise '''
    status_code = resp['ResponseMetadata']['HTTPStatusCode']
    status_bool = True if status_code is 200 else False
    return status_bool, status_code


def pickle_save(all_things_obj, filename=PICKLE_STORE_NAME):
    ''' Pickle the all things obj '''
    with open(filename, 'wb') as fh:
        pickle.dump(all_things_obj, fh)


def pickle_load(filename=PICKLE_STORE_NAME):
    ''' Load all things obj from pickle and return '''
    with open(filename, 'rb') as fh:
        all_things_obj = pickle.load(fh)
    return all_things_obj



# For some local testing and development
if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    test_thing_type_name = 'cam_type'
    iot_all_things = aws_iot_all_things()
    aws_thing_type = aws_iot_thing_type()

    '''
    test_thing_name = 'gg_test_thing_01'
    resp = iot_all_things.create_thing(test_thing_name, test_thing_type_name)
    print(resp)

    print(iot_all_things.iot_things_list)
    print(iot_all_things.iot_things_objs)

    # pickle_save(iot_all_things)

    test_thing_name = 'gg_test_thing_01'
    resp = iot_all_things.delete_thing(test_thing_name)
    print(resp)

    print(iot_all_things.iot_things_list)
    print(iot_all_things.iot_things_objs)
    '''

    resp, _ = iot_all_things.list_all_things()
    print(resp)

    
    ##### Temp stuff below to create some default types and test it too
    '''
    # Create cam type
    properties = {
                   'thingTypeDescription': 'Camera Type for project Neutrino',
                   'searchableAttributes': [
                     'camera', 'cam',
                    ]
                 }
    tags=[
           {
             'Key': 'type', 'Value': 'camera'
           },
       ]
    resp = aws_thing_type.create_thing_type('cam_type', 
                                      properties=properties, tags=tags)
    print(resp)
    ###### test create_thing_type #############
    # resp = aws_thing_type.create_thing_type('test_type')
    # print(resp)

    ###### test delete_thing_type #############
    # First deprecate
    # resp = aws_thing_type.deprecate_thing_type('test_type')
    # print(resp)
    
    # Then delete
    # Need to wait 5 min after deprecate then delete
    # resp = aws_thing_type.delete_thing_type('test_type')
    # print(resp)
    '''

    '''
    resp, _ = aws_thing_type.list_all_thing_types()
    print(resp)
    for r in resp:
        rv = aws_thing_type.get_thing_type_properties(r)
        print(rv)
    '''

