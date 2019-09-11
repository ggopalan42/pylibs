''' This defines a bunch of functions that are useful for using AWS DynamoDB '''

import os
import boto3
import logging

from botocore.exceptions import ClientError

from pylibs.cloud.aws.config import aws_settings
from pylibs.cloud.aws.config import aws_exceptions
from pylibs.cloud.aws.common import aws_common_utils

# Constants

# Set logging level
# logging.basicConfig(level=logging.INFO)


def create_table(table_name, table_schema, primary_key, secondary_key=None, 
                 billing_mode='PAY_PER_REQUEST', other_attributes={},
                 aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' Create a DynamoDB table

        Arguments:
            - table_name:  Name of table. Name needs to follow AWS name rules
            - table_schema: The schema of the table specified as a list of
                            dicts. See example way below in the file.
                            At the very least, the primary (and the optional 
                            secondary) key schemas need to be defines
            - primary_key:  The indexing key
            - secondary_key: The optional sorting key
            - billing_mode: Default is PAY_PER_REQUEST. Set to a dictionary
                            per API if other modes are needed
            - other_attributes: Other attributes as a dict. Currently not
                                implemented
        Returns:
            - table_arn: The ARN of the created table
            - table_id: The ID of the created table
            - table_description: The full JSON response from AWS 
                                 (minus the response metadata)
    '''
    dyndb_client = boto3.client('dynamodb')

    # Define the attributes definition dict outside the create_table call.
    # This is because primary and secondary key types have to be specified
    # and then this dict updated with any other attributes
    # Also making implicit asumption here that pri key is string and 
    # sec key is numerical. More coding needed if more flexibiliuty is needed

    # Now update it with any other attributes
    # attrs_definition.update(other_attributes)

    table = dyndb_client.create_table(
                TableName = table_name,
                KeySchema = [
                    {
                        'AttributeName': primary_key,
                        'KeyType': 'HASH'     # HASH = primary key in AWS land
                    }, 
                    {
                        'AttributeName': secondary_key,
                        'KeyType': 'RANGE'    # RANG = sort key in AWS land
                    } if secondary_key else {}
               ],
               AttributeDefinitions = [
                    {
                        'AttributeName': primary_key,
                        'AttributeType': 'S'   
                    },
                    {
                        'AttributeName': secondary_key,
                        'AttributeType': 'N'    
                    } if secondary_key else {}
               ],
               BillingMode = billing_mode
           )

    sbool, scode = aws_common_utils.check_response_status(table)
    if not sbool:
        logging.info(f'AWS API call to create DynamoDB '
        f'table {table_name} failed with code: {scode}')
        raise aws_exceptions.AWS_API_CallFailed

    # Return the table ARN, table ID and the entire response
    table_arn = table['TableDescription']['TableArn']
    table_id = table['TableDescription']['TableId']
    return table_arn, table_id, table['TableDescription']


def delete_table(table_name, aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' Delete a DynamoDB table

        Arguments:
            - aws_region: AWS region from which to list tables
                          Currently unused
            - table_name: Table name to delete

        Returns:
            - deleted_table_name: Name of deleted table (taken from response)
            - full_response: The full JSON response of the AWS call
                             (minus the response metadata)
                             This appears to be the table description
    '''
    dyndb_client = boto3.client('dynamodb')

    resp = dyndb_client.delete_table(TableName = table_name)
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to delete DynamoDB table failed '
                     f'with code: {scode}')
        raise aws_exceptions.AWS_API_CallFailed

    deleted_table_name = resp['TableDescription']['TableName']

    return deleted_table_name, resp['TableDescription']


def list_tables(aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' List all DynamoDB in current AWS region
        ###### Mega Note: ######
            This code does not use pagination. As such, the first 100
            tables *ONLY* are returned. If there are more than 100 tables,
            code needs to be extended like the list lambda functions

        Arguments:
            - aws_region: AWS region from which to list tables
                          Currently unused
        Returns:
            - table_names: A list of table names
    '''
    dyndb_client = boto3.client('dynamodb')

    resp = dyndb_client.list_tables()
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to list DynamoDB table failed '
                     f'with code: {scode}')
        raise aws_exceptions.AWS_API_CallFailed

    return resp['TableNames'] 

def describe_table(table_name, aws_region=aws_settings.AWS_DEFAULT_REGION):
    ''' Describe a table in AWS DynamoDB

        Arguments:
            - aws_region: AWS region from which to list tables
                          Currently unused
            - table_name: Name of table to describe

        Returns:
            - table_description: JSON describing the table. Pretty much the
                                 JSON returned by the AWS boto3 call
    '''
    dyndb_client = boto3.client('dynamodb')

    resp = dyndb_client.describe_table(TableName = table_name)
    sbool, scode = aws_common_utils.check_response_status(resp)
    if not sbool:
        logging.info(f'AWS API call to describe DynamoDB table failed '
                     f'with code: {scode}')
        raise aws_exceptions.AWS_API_CallFailed

    return resp['Table']

 
if __name__ == '__main__':

    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        cmd = 'l'

    # For testing
    table_name = 'gg_test1'
    primary_key = 'gg_test1_pri'
    secondary_key = 'gg_test1_sec'
    gg_test1_table_schema = [
        {
            'AttributeName': 'gg_test1_pri',
            'AttributeType': 'S'      # S = String
        },
        {
            'AttributeName': 'gg_test1_sec',
            'AttributeType': 'N'      # N = Number
        },
    ] 

    if cmd == 'a':
        resp = create_table(table_name, gg_test1_table_schema, 
                     primary_key, secondary_key)
        print(resp)
    elif cmd == 'd':
        resp = delete_table(table_name)
        print(resp)
    elif cmd == 'l':
        resp = list_tables()
        print(resp)
    elif cmd == 's':
        resp = describe_table(table_name)
        print(resp)
    else:
        resp = list_tables()
        print(resp)
