''' This defines a bunch of functions that are useful for using AWS S3 '''

import os
import boto3
import logging

from botocore.exceptions import ClientError

from pylibs.cloud.aws.config import aws_settings
from pylibs.cloud.aws.config import aws_s3_settings
from pylibs.cloud.aws.config import aws_exceptions
from pylibs.cloud.aws.common import aws_common_utils

# Constants
# Below particular format needed by boto3 API
# And setting it to default region for now
DEFAULT_BUCKET_REGION = {'LocationConstraint': aws_settings.AWS_DEFAULT_REGION}

# Set logging level
logging.basicConfig(level=logging.INFO)


 
################ Bucket Utils ######################
def put_object(dest_bucket_name, dest_object_name, src_data, 
               aws_region=aws_settings.AWS_DEFAULT_REGION):
    '''Add an object to an Amazon S3 bucket

       Arguments:
           - dest_bucket_name: obvious what it is
           - dest_object_name: obvious what it is
           - src_data: The src_data argument must be of type bytes or a 
                       string that references a file specification.

       Returns: Success or Failure codes
    '''
    # If a region other than default region is specified, raise an error
    if aws_region != aws_settings.AWS_DEFAULT_REGION:
        raise aws_exceptions.AWS_RegionNotImplemented


    # Construct the object data to be put
    if isinstance(src_data, bytes):
        object_data = src_data
    elif isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            logging.error(e)
            return aws_s3_settings.S3_PUT_OBJECT_FAIL
    else:
        logging.error('Type of {} for the argument \'src_data\' is '
                      'not supported.'.format(str(type(src_data))))
        return aws_s3_settings.S3_PUT_OBJECT_FAIL

    # Put the object
    s3_client = boto3.client('s3')
    try:
        s3_client.put_object(Bucket=dest_bucket_name, Key=dest_object_name, 
                             Body=object_data)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error==(dest bucket/obj == src bucket/obj)
        logging.error(e)
        return aws_s3_settings.S3_PUT_OBJECT_FAIL
    finally:
        if isinstance(src_data, str):
            object_data.close()
    return aws_s3_settings.S3_PUT_OBJECT_SUCCESS


def list_s3_objects(bucket_name, aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' List all buckets in requested region

        Arguments:
            - bucket_name: List objects in bucket_name
            - aws_region: List buckets in this region
                    Note: Currently only the AWS_DEFAULT_REGION is implemented
        Returns:
            - A list of objects
    '''
    # If a region other than default region is specified, raise an error
    if aws_region != aws_settings.AWS_DEFAULT_REGION:
        raise aws_exceptions.AWS_RegionNotImplemented

    obj_name_list = []
    obj_full_list = []
    s3_client = boto3.client('s3')

    # pagination is used in case there are > 1000 objects
    paginator = s3_client.get_paginator('list_objects')
    pages = paginator.paginate(Bucket=bucket_name)

    for page in pages:
        # Check needed in case there are no objects in bucket
        if 'Contents' in page:
            for obj in page['Contents']:
                obj_name_list.append(obj['Key'])
                obj_full_list.append(obj)
    return obj_name_list, obj_full_list
   

def create_s3_bucket(bucket_name, ACL='', 
                     CreateBucketConfiguration=DEFAULT_BUCKET_REGION):
    ''' Create an S3 bucket if it does not already exist

        Arguments:
          - bucket_name: Bucket name (string)
          - ACL: Access control. See boto3 documentation
          - CreateBucketConfiguration: For more fine control. 
                                       See boto3 documentation 
    '''
    # First check if bucket already exists
    buckets, _ = list_s3_buckets()
    if bucket_name in buckets:
        logging.info(f'Bucket name: {bucket_name} already exists.')
        return aws_s3_settings.S3_BUCKET_ALREADY_EXISTS
    else:
        logging.info(f'Creating bucket: {bucket_name}')
        s3_client = boto3.client('s3')
        try:
            # Try creating a bucket with given name
            response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=CreateBucketConfiguration)
        except ClientError as e:
            # If bucket name exists in region (for any user), boto3 throws
            # a BucketAlreadyExists error and below seems to be the standard
            # way to handle this
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                # Then print the standard exception as it appears to have
                # the best explanation
                logging.error(f'Bucket name: {bucket_name} already exists '
                                 'in this region')
                logging.error(e) 
            else:
                logging.error('Unexpected error occured')
                logging.error(e)
            return aws_s3_settings.S3_CREATE_BUCKET_FAILED
        sbool, scode = aws_common_utils.check_response_status(response)
        if not sbool:
            logging.info(f'AWS API call to S3 list buckets failed with code: '
                         f'{scode}')
            raise aws_exceptions.AWS_API_CallFailed
            return aws_s3_settings.S3_CREATE_BUCKET_FAILED
        else:
            logging.info(f'Successfully created bucket: {bucket_name}')
            return aws_s3_settings.S3_CREATE_BUCKET_SUCCESS


def list_s3_buckets(aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' List all buckets in requested region

        Arguments:
            - aws_region: List buckets in this region
                    Note: Currently only the AWS_DEFAULT_REGION is implemented
        Returns:
            - A list of bucket names
    '''

    # If a region other than default region is specified, raise an error
    if aws_region != aws_settings.AWS_DEFAULT_REGION:
        raise aws_exceptions.AWS_RegionNotImplemented

    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    # Check if call succeded
    status_bool, status_code = aws_common_utils.check_response_status(response)
    if not status_bool:
        logging.info(f'AWS API call to S3 list buckets failed with code: '
                     f'{status_code}')
        raise aws_exceptions.AWS_API_CallFailed
    full_list = response['Buckets']
    names_list = [x['Name'] for x in full_list]
    return names_list, full_list


def delete_s3_bucket(bucket_name, aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' Delete bucket in requested region

        Arguments:
            - bucket_name: name of bucket to delete
            - aws_region: Delete bucket in this region
                    Note: Currently only the AWS_DEFAULT_REGION is implemented
        Returns:
            - Success or error code
    '''

    # If a region other than default region is specified, raise an error
    if aws_region != aws_settings.AWS_DEFAULT_REGION:
        raise aws_exceptions.AWS_RegionNotImplemented

    s3_client = boto3.client('s3')
    try:
        response = s3_client.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        # If an error is thrown, then this is standard way to handle this
        if e.response['Error']['Code'] == 'NoSuchBucket':
            # Then print the standard exception as it appears to have
            # the best explanation
            logging.error(f'No such bucket name: {bucket_name}')
            logging.error(e) 
        else:
            logging.error('Unexpected error occured')
            logging.error(e)
        return aws_s3_settings.S3_BUCKET_DELETE_FAILED

    # Check if call succeded
    status_bool, status_code = aws_common_utils.check_response_status(response)
    if not status_bool:
        logging.info(f'AWS API call to S3 list buckets failed with code: '
                     f'{status_code}')
        raise aws_exceptions.AWS_API_CallFailed
        return aws_s3_settings.S3_BUCKET_DELETE_FAILED
    else:
        logging.info(f'Bucket: {bucket_name} successfully deleted')
        return aws_s3_settings.S3_BUCKET_DELETE_SUCCESS


# For some local testing and development
if __name__ == '__main__':
    '''
    names, full = list_s3_buckets()
    print(names)
    print(full)

    resp = create_s3_bucket('duckduck-test6')
    print(resp)

    resp = delete_s3_bucket('duckduck-test6')
    print(resp)
    '''

    '''
    objs, full = list_s3_objects('testbucket-l1')
    # objs, full = list_s3_objects('neutrino-unique1')
    print(objs)
    print(full)
    '''

    resp = put_object('neutrino-unique1', 'dingaling.py', 's3_utils.py')
    print(resp)
