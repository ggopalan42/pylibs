''' This file hosts functions common to many AWS services '''

def check_response_status(resp):
    ''' This will check if the status code of response of a AWS IoT Core
        API call is 200 and will return True if it is and false otherwise '''
    status_code = resp['ResponseMetadata']['HTTPStatusCode']
    status_bool = True if status_code is 200 else False
    return status_bool, status_code

