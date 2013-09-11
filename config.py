'''
    Software configuration. It is an executable Python file and is
    imported for access to the variables.
'''

import os.path

# Identity verification through Mozilla Persona requires the hostname to
# be sent in the checking request.

import platform

if platform.node() == 'pyweb':
    hostname = '16plus.jsb.be'
    DATA_PATH = os.path.expanduser('~') + '/apps/16plus.jsb.be-stable/data'
    repository_latest = os.path.expanduser('~') + '/app/16plus.jsb.be-latest'
else:
    hostname = 'localhost:1616'
    if platform.node() == 'lithium':
        DATA_PATH = os.path.expanduser('~') + '/Desktop/16plus.jsb.be-stable/data'
        repository_latest = os.path.expanduser('~') + '/Desktop/16plus.jsb.be-latest'
    else:
        DATA_PATH = os.path.expanduser('~') + '/Documents/Projects/Python/16plus.jsb.be/data'
        repository_latest = None
    
REGISTRATIONS_PATH = DATA_PATH + '/registrations'
JSON_PATH = DATA_PATH + '/json'
