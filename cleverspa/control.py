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

    def set_data(self, did, attrs):
        req = requests.post(f'{API_URL}/control/{did}', headers=self.headers, json={'attrs':attrs})
        if req.ok:
            return True
        return False

    def set_temp(self, did, temp):
        return self.set_data(did, {'Temperature_setup': temp})
    '''
    def set_filter_on(self, did):
        return self.set_data(did, {'Filter':1})
    
    def set_filter_off(self, did):
        return self.set_data(did, {'Filter':0})

    def set_heater_on(self, did):
        return self.set_data(did, {'Heater':1, 'Filter':1})
    
    def set_heater_off(self, did):
        return self.set_data(did, {'Heater':0, 'Filter':0})

    def set_bubbles_on(self, did):
        return self.set_data(did, {'Bubble':1})
    
    def set_bubbles_off(self, did):
        return self.set_data(did, {'Bubble':0})
    '''
