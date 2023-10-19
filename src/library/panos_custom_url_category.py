#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'support_by': 'community'
}

DOCUMENTATION = '''
---
module: panos_custom_url_category

short_description: Manages custom URL filter categories for PANOS

description:
    - "Module for managing custom URL filter categories for PANOS"

dependencies:
    - pan-python

options:
    - api_key:
        description:
            - Used for authenticating against PANOS XML API
        required: true
    - state:
        description:
            - Sets the state of the custom URL category
        choices:
            - present
            - absent
            - query
    - hostname:
        description:
            - The hostname of PANOS endpoint
        required: true
    - urls
        description:
            - A list of URLs to add to the custom URL category. Wildcards can be used.
        type: list
    - description:
        description:
            - Gives the custom URL category a description
    - ignore_cert_error:
        description:
            - This will ignore errors
...
'''

EXAMPLES = '''
  + module.params['description'] + allowed list custom url category
  delegate_to: localhost
  panos_custom_url_category:
    api_key: "{{ panos_api_key }}"
    state: present
    hostname: "{{ panos_hostname }}"
    urls:
      - "www.google.com"
      - "*.microsoft.com"
    description: "default allowed list"
    ignore_cert_error: true
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.igs.panos import PanosClient, PanosClientError, should_update

def build_member_list(entries):
    collected = []
    for entry in entries:
        collected.append("<member>" + entry + "</member>")
    print(''.join(collected))
    return ''.join(collected)

def get_entries(panos, xpath):
    data = panos.get(xpath)
    if data['response']['code'] == '19':
        for e in data['response']['result']['entry']:
            result = {
                "name": e['name'],
                "description": e['description']
            }
            result['members'] = []
            for member in e['list']['member']:
                result['members'].append(member)
            return result
    else:
        return None

def run_module():
    module_args = dict(
        api_key=dict(type='str', required=True),
        state=dict(
            type='str',
            required=False,
            default="query",
            choices=['present', 'absent', 'query']),
        name=dict(type='str', required=True),
        description=dict(type='str', required=False),
        hostname=dict(type='str', required=True),
        device_name=dict(type='str', required=False, default="localhost.localdomain"),
        virtual_system=dict(type='str', required=False, default="vsys1"),
        urls=dict(type='list', required=False),
        ignore_cert_error=dict(type='bool', required=False),
        commit=dict(type='bool', default=False)
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

    base_xpath = (
        "/config/devices/entry[@name='"
        + module.params['device_name'] +
        "']/vsys/entry[@name='"
        + module.params['virtual_system'] +
        "']/profiles/custom-url-category/"
    )

    xpath = base_xpath + "entry[@name='" + module.params['name'] + "']"

    try:
        panos = PanosClient(
            api_key=module.params['api_key'],
            hostname=module.params['hostname'],
            ignore_cert_error=module.params['ignore_cert_error']
        )
    except PanosClientError as e:
        module.fail_json(msg=e)

    if module.params['state'] == 'query':
        try:
            data = get_entries(panos, xpath)
            result['changed'] = False
            result['data'] = data
            module.exit_json(**result)
        except Exception as e:
            result['error'] = "test"
            module.fail_json(**result)
    if module.params['state'] == 'absent':
        try:
            if get_entries(panos, xpath):
                panos.delete(xpath)
                if module.params['commit']:
                    panos.commit()
                result['changed'] = True
                module.exit_json(**result)
            else:
                result['changed'] = False
                module.exit_json(**result)
        except Exception as e:
            module.fail_json(msg=e)

    current = get_entries(panos, xpath)
    element = ("<description>" + module.params['description'] + "</description><list>"
            + build_member_list(module.params['urls']) +
            "</list>"
            )
    if current:
        update, changes = should_update(current['members'], module.params['urls'])
        if update:
            try:
                panos.edit(xpath + '/list',
                        "<list>" + build_member_list(module.params['urls']) + "</list>"
                )
                if module.params['commit']:
                    panos.commit()
                result['changed'] = True
                result['changes'] = changes
                module.exit_json(**result)
            except Exception as e:
                module.fail_json(msg=e)
        else:
            try:
                result['changed'] = False
                module.exit_json(**result)
            except Exception as e:
                module.fail_json(msg=e)
    else:
        try:
            panos.set(xpath, element)
            if module.params['commit']:
                panos.commit()
            result['changed'] = True
            module.exit_json(**result)
        except Exception as e:
            module.fail_json(msg=e)

def main():
    run_module()

if __name__ == '__main__':
    main()
