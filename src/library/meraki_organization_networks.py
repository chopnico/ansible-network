#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'support_by': 'community'
}

DOCUMENTATION = '''
---
module: meraki_organization_networks

short_description: Queries for Meraki organization networks

description:
    - "A Meraki module for querying the Meraki dashboard API for organization networks"

options:
    auth_key:
        description:
            - A Meraki dashboard API key that will be used for authentication
        required: true
    state:
        description:
            - Unnecessary as it will only query, but it's here regardless
    org_id:
        description:
            - The Meraki organization id where networks live
        required: true
    tag:
        description:
            - If a tag is specified, it will only query for networks with the specified tag
'''

EXAMPLES = '''
- name: get production networks
  delegate_to: localhost
  meraki_organization_networks:
     auth_key: "{{ meraki_api_key }}"
     state: query
     org_id: "12345"
     tag: "production"
'''

from ansible.module_utils.basic import AnsibleModule
from meraki_sdk.meraki_sdk_client import MerakiSdkClient
from meraki_sdk.exceptions.api_exception import APIException

MERAKI_API_URL = "https://api.meraki.com/api/v0/networks/"

def get_networks(client, organization_id):
    options = { 'organization_id': organization_id }
    return client.networks.get_organization_networks(options)

def get_networks_by_tag(client, organization_id, tag):
    options = { 'organization_id': organization_id }
    networks = client.networks.get_organization_networks(options)

    collected = []
    for network in networks:
        if network['tags']:
            if tag in network['tags']:
                collected.append(network)
    return collected

def run_module():
    module_args = dict(
        auth_key=dict(type='str', required=True),
        state=dict(type='str', required=False, default='query'),
        org_id=dict(type='str', required=True),
        tag=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    try:
        meraki_client = MerakiSdkClient(module.params['auth_key'])
        networks = get_networks_by_tag(meraki_client, module.params['org_id'], module.params['tag'])
        result['changed'] = False
        result['data'] = networks
        module.exit_json(**result)
    except:
        module.fail_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
