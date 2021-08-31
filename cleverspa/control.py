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

    def get_device(self, did):
        devices = self.get_devices()
        try:
            device = next(device for device in devices if device['did'] == did)
        except KeyError:
            device = False
        return device

    def get_data(self, did):
        req = requests.get(f'{API_URL}/devdata/{did}/latest', headers=self.headers)
        return req.json()['attr']

    def set_data(self, did, payload):
        errors = 0
        for k,v in payload.items():
            req = requests.post(
                    f'{API_URL}/control/{did}',
                    headers=self.headers,
                    json={
                        'attrs':{k:v}
                    }
            )
            if not req.ok:
                errors += 1
        if errors:
            return False
        return True

    def set_temp(self, did, temp):
        return self.set_data(did, {'Temperature_setup': temp})

