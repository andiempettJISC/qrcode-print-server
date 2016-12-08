import os
import yaml

conf_file = (os.path.abspath(os.path.join(os.path.dirname(__file__), 'conf.yaml')))

conf = yaml.load(open(conf_file))

def get_user():
    return conf['username']

def get_password():
    return conf['password']

def get_host():
    return conf['host']

def get_port():
    return conf['port']

def get_printer():
    return conf['printer_name']

def jira_url():
    return conf['jira_url']

def jira_user():
    return conf['jira_username']

def jira_pass():
    return conf['jira_password']

def get_msg():
    return conf['custom_message']
