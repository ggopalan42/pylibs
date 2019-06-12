''' This file contains various settings, defaults and other such items
    needed to run things on aws '''

# Not sure if this is the correct location for the project name
# constant, but going with it for now
AWS_PROJECT_NAME = 'neutrino'

AWS_DEFAULT_REGION = 'us-west-2'     # This is Oregon

AWS_SECURITY_GROUPS = {
    'neutrino': 'sg-05811705b74edb37e',
    'default': 'sg-8c12d0fe',
}

AWS_REGIONS = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "ca-central-1": "Canada (Central)",
    "eu-west-1": "EU (Ireland)",
    "eu-central-1": "EU (Frankfurt)",
    "eu-west-2": "EU (London)",
    "eu-west-3": "EU (Paris)",
    "eu-north-1": "EU (Stockholm)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "ap-northeast-2": "Asia Pacific (Seoul)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "sa-east-1": "South America (São Paulo)",
    "us-gov-west-1": "US Gov West 1",
    "us-gov-east-1": "US Gov East 1",
}
