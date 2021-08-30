DOMAIN = 'cleverspa'
MANUFACTURER = 'CleverSpa'
DEFAULT_NAME = 'CleverSpa'


CONF_DID = 'did'
CONF_TOKEN = 'token'
CONF_MODEL = 'product_name'
CONF_SWVER = 'mcu_soft_version'
CONF_DEVICE = 'device'
CONF_DEVICE_INFO = 'device_info'

MAP_NAMES = {
    'filter_time':'Time_filter',
    'filter_warning':'Overtime_filter',
    'freeze_warning':'Undercooling',
    'overheat_warning':'Superheat',
    'target_temperature': 'Temperature_setup',
    'current_temperature': 'Current_temperature',
    'filter': 'Filter',
    'bubbles': 'Bubble',
    'heater': 'Heater'
}

MIN_TEMP = 20
MAX_TEMP = 42
