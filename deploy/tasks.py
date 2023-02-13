#last updated: 08-02-2023
from pprint import pprint
import urllib3
import requests
import yaml
import json
import settings
import os


failed_out = '''
# COMMAND: \033[33m{}\033[m
# SUCCESS: \033[31m{}\033[m
# ERROR:   \033[31m{}\033[m
# RESULT:
{}
'''

success_out = '''
# COMMAND: \033[33m{}\033[m
# SUCCESS: \033[32m{}\033[m
'''

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def notify(text, align='^'):
    if align == '^':
        return '{:#^100s}'.format('  ' + text + '  ')
    elif align == '<':
        return '{:-<10s}'.format(' ' + text + '  ')
    elif align == '-':
        return '{:-<0s}'.format('\033[44mRESULT\033[m ' + text + ' ')
    elif align == '>':
        return '{:-^100s}'.format(' \033[34m' + text + '\033[m ')
    else:
        raise ValueError('Only ^ , - , > and < are supported')

def prepare_payload(command_list, api_key):
    schema = {'op': None, 'path': None}
    payloads = []
    for command in command_list:
        schema = {'op':"set",'path': command}
        payloads.append(schema)

    to_push = {}
    to_push["data"] = (None, (json.dumps(payloads)))
    to_push["key"] = (None,  getattr(settings, api_key))
    return to_push

def apply(target, port, command_list, api_key):
    payloads = prepare_payload(command_list, api_key)
    endpoint = "configure"
    port_number = getattr(settings, port)
    url = 'https://{}:{}/{}'.format(target, port_number, endpoint)

    result = requests.post(url, files=payloads, verify=False)
    print(show_result(command_list[0][0].upper() +" " + command_list[0][1].upper() + " CONFIGURATIONS", json.loads(result.text)))

def show_result(command, result):
    if isinstance(result['data'], str):
        outcome = result['data'].splitlines()
    else:
        outcome = result['data']

    if result['success'] == True:
         return success_out.format(command,
                         result['success'],
                         pprint(outcome, width=120))
    else:
        return failed_out.format(command,
                         result['success'],
                         result['error'],
                         pprint(outcome, width=120))

def save_config(target, port, api_key): 
    to_push = {}
    data = {"op": "save"}
    to_push["data"] = (None, (json.dumps(data)))
    to_push["key"] = (None, getattr(settings, api_key))
    port_number = getattr(settings, port)
    url = 'https://{}:{}/config-file'.format(target, port_number)
    result = requests.post(url, files = to_push, verify=False)
    return json.loads(result.text)

def parse_yaml(filename):
    data_file_path = os.path.join(os.path.dirname(__file__), filename)
    print(data_file_path)
    with open(data_file_path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    return result
