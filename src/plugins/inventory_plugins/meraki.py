import os
import urllib3
import json

from ansible.plugins.inventory import BaseInventoryPlugin

DASHBOARD_API_URL = "https://api.meraki.com/api/v0/"
ANSIBLE_ENVIRONMENT = os.environ['ANSIBLE_ENVIRONMENT']

class InventoryModule(BaseInventoryPlugin):
    NAME = "meraki"

    def __init__(self):
        super(InventoryModule, self).__init__()

    def _get_networks_by_organization(self, api_key, organization_id):
        http = urllib3.PoolManager()

        networks = json.loads(http.request(
            'GET',
            DASHBOARD_API_URL + "/organizations/" + organization_id + "/networks",
            headers={
                'X-Cisco-Meraki-API-Key': api_key
            }
        ).data)

        return networks

    def _filter_networks_by_tag(self, networks, tag):
        networks_by_tag = []
        for network in networks:
            if network['tags'] is not None:
                if tag in network['tags']:
                    networks_by_tag.append(network)

        return networks_by_tag

    def verify_file(self, path):
        valid = False

        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('meraki.yml', 'meraki.yaml')):
                valid = True

        return valid
   
    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        config_data = self._read_config_data(path)
        self.inventory.add_group("meraki")

        http = urllib3.PoolManager()

        meraki_secrets = json.loads(http.request(
            'GET',
            os.environ['VAULT_ADDR'] + "/v1/secret/" + ANSIBLE_ENVIRONMENT + "/ansible/meraki",
            headers={
                'X-Vault-Token': os.environ['VAULT_TOKEN']
            }
        ).data)

        organization_id = meraki_secrets['data']['organization_id']
        api_key = meraki_secrets['data']['api_key']

        networks = self._get_networks_by_organization(api_key, organization_id)
        networks_by_tag = self._filter_networks_by_tag(networks, ANSIBLE_ENVIRONMENT)

        for network in networks_by_tag:
            self.inventory.add_host(network['name'], group="meraki")
            self.inventory.set_variable(network['name'], 'network_id', network['id'])
            self.inventory.set_variable(network['name'], 'meraki_api_key', api_key)
            self.inventory.set_variable(network['name'], 'meraki_organization_id', organization_id)
