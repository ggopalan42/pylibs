''' This file contains AWS error codes and associalted messages '''

# AWS API Call Error Codes
AWS_NO_ERROR = 0
AWS_IAM_ROLE_ALREADY_EXISTS = 1
AWS_IAM_ROLE_DOES_NOT_EXIST = 2


AWS_ERROR_MESSAGES = {
    AWS_NO_ERROR : 'No error', 
    AWS_IAM_ROLE_ALREADY_EXISTS: 'AWS IAM Role Already Exists',
    AWS_IAM_ROLE_DOES_NOT_EXIST: 'AWS IAM Role Does Not Exist',
}

def msg_from_code(err_code):
    ''' Return error message for error code '''
    if err_code in AWS_ERROR_MESSAGES.keys():
        return AWS_ERROR_MESSAGES[err_code]
    else:
        return f'Error code {err_code} does not exist'


def construct_response(err_code):
    ''' Return a dictionary with the appropriate error fields set '''
    resp = {
             'Error': True,   
             'Error Code': err_code,
             'Error message': msg_from_code(err_code)
           }
    return resp
