"""Constants for the digitalSTROM VDC integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "digitalstrom_vdc"

# Configuration and options
CONF_PORT: Final = "port"
CONF_VDC_NAME: Final = "vdc_name"
CONF_DSUID: Final = "dsuid"
CONF_SERVICE_NAME: Final = "service_name"
CONF_ANNOUNCE_SERVICE: Final = "announce_service"

# Defaults
DEFAULT_PORT: Final = 8444
DEFAULT_VDC_NAME: Final = "Home Assistant VDC"
DEFAULT_SERVICE_NAME: Final = "ha-vdc"
DEFAULT_ANNOUNCE_SERVICE: Final = True

# Connection states
STATE_DISCONNECTED: Final = "disconnected"
STATE_CONNECTING: Final = "connecting"
STATE_CONNECTED: Final = "connected"
STATE_ACTIVE: Final = "active"

# Device creation methods
DEVICE_METHOD_TEMPLATE: Final = "template"
DEVICE_METHOD_MANUAL: Final = "manual"

# Binding types
BINDING_TYPE_OUTPUT: Final = "output"
BINDING_TYPE_INPUT: Final = "input"
BINDING_TYPE_SENSOR: Final = "sensor"
BINDING_TYPE_BINARY_INPUT: Final = "binary_input"

# Update intervals
SCAN_INTERVAL: Final = 30  # seconds

# Service names
SERVICE_ANNOUNCE_DEVICE: Final = "announce_device"
SERVICE_CALL_SCENE: Final = "call_scene"
SERVICE_SAVE_SCENE: Final = "save_scene"
SERVICE_REFRESH_TEMPLATES: Final = "refresh_templates"

# Attributes
ATTR_DEVICE_ID: Final = "device_id"
ATTR_SCENE_NUMBER: Final = "scene_number"
ATTR_FORCE: Final = "force"

# Platforms
PLATFORMS: Final = [
    "light",
    "switch",
    "sensor",
    "binary_sensor",
    "cover",
    "climate",
    "button",
]

# Error messages
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_INVALID_PORT: Final = "invalid_port"
ERROR_PORT_IN_USE: Final = "port_in_use"
ERROR_UNKNOWN: Final = "unknown"
ERROR_DSS_HANDSHAKE_FAILED: Final = "dss_handshake_failed"
ERROR_INVALID_DSUID: Final = "invalid_dsuid"

# Config flow steps
STEP_USER: Final = "user"
STEP_VDC_INIT: Final = "vdc_init"
STEP_ZEROCONF_SETUP: Final = "zeroconf_setup"
STEP_DSS_CONNECT: Final = "dss_connect"

# Options flow steps
STEP_INIT: Final = "init"
STEP_ADD_DEVICE: Final = "add_device"
STEP_TEMPLATE_SELECT: Final = "template_select"
STEP_TEMPLATE_CONFIGURE: Final = "template_configure"
STEP_MANUAL_DEVICE: Final = "manual_device"
STEP_ADD_INPUTS: Final = "add_inputs"
STEP_ADD_OUTPUT: Final = "add_output"
STEP_ADD_CHANNEL: Final = "add_channel"
STEP_FINALIZE_DEVICE: Final = "finalize_device"

# Device template types
TEMPLATE_TYPE_DEVICE: Final = "deviceType"
TEMPLATE_TYPE_VENDOR: Final = "vendorType"

# Data keys
DATA_VDC_MANAGER: Final = "vdc_manager"
DATA_COORDINATOR: Final = "coordinator"
DATA_DEVICE_MANAGER: Final = "device_manager"
DATA_TEMPLATE_MANAGER: Final = "template_manager"
DATA_BINDINGS: Final = "bindings"
