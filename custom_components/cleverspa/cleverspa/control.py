import requests
from .const import API_URL, APP_ID

class control:

    def __init__(self, token):
        self.headers = {
            'X-Gizwits-Application-Id': APP_ID,
            'X-Gizwits-User-token': token
        }

    def get_devices(self):
        req = requests.get(f'{API_URL}/bindings', headers=self.headers)
        res = req.json()
        try:
            devices = res['devices']
        except KeyError:
            devices = False
        return devices

    def get_data(self, did):
        req = requests.get(f'{API_URL}/devdata/{did}/latest', headers=self.headers)
        return req.json()['attr']

    def set_data(self, did, payload):
        errors = 0
        for payload_attr in payload:
            req = requests.post(
                    f'{API_URL}/control/{did}',
                    headers=self.headers,
                    json={
                        'attrs': payload_attr
                    }
            )
            if not req.ok:
                errors += 1
        if errors:
            return False
        return True

