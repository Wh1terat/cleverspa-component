DOMAIN = 'cleverspa'
PLATFORMS = [
    'sensor',
    'binary_sensor',
    'switch',
    'water_heater'
]
MANUFACTURER = 'CleverSpa'
DEFAULT_NAME = 'CleverSpa'
MIN_TEMP = 20
MAX_TEMP = 42
COOLDOWN_TIME = 30

CONF_DEVICE_INFO = 'device_info'

MAP_KEYS = {
    'Time_filter':'filter_time',
    'Overtime_filter':'filter_warning',
    'Undercooling':'freeze_warning',
    'Superheat':'overheat_warning',
    'Temperature_setup':'target_temperature',
    'Current_temperature':'current_temperature',
    'Filter':'filter',
    'Bubble':'bubbles',
    'Heater':'heater',
    # bindings
    'mcu_soft_version': 'sw_version',
    'product_name': 'model',
    'did': 'device_id',
    'dev_label': 'friendly_name'
}

MAP_KEYS_INV = {v: k for k, v in MAP_KEYS.items()}

