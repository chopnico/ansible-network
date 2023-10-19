#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'support_by': 'community'
}

DOCUMENTATION = '''
'''

EXAMPLES = '''
'''

from ansible.module_utils.basic import AnsibleModule

import requests
import re
import urllib3

urllib3.disable_warnings()

def run_module():
    module_args = dict(
        url=dict(type='str', required=True),
        state=dict(type='str', required=False, default="query"),
        validate_certs=dict(type='bool', required=False, default=False)
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

    if module.params['state'] == 'query':
        try:
            feed = requests.get(module.params['url'], verify=module.params['validate_certs'])

            result['data'] = []
            for address in feed.text.split("\n"):
                if address != "":
                    ip_range = address.split("-")
                    if(ip_range[0] == ip_range[1]):
                        result['data'].append(f"{ip_range[0]}/32")
                    else:
                        result['data'].append(f"{ip_range[0]}/24")
            result['changed'] = False
            module.exit_json(**result)
        except Exception as e:
            module.fail_json(msg=e)

def main():
    run_module()

if __name__ == "__main__":
    main()
