"""Config flow for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
import socket
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_ANNOUNCE_SERVICE,
    CONF_DSUID,
    CONF_PORT,
    CONF_SERVICE_NAME,
    CONF_VDC_NAME,
    DEFAULT_ANNOUNCE_SERVICE,
    DEFAULT_PORT,
    DEFAULT_SERVICE_NAME,
    DEFAULT_VDC_NAME,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    ERROR_DSS_HANDSHAKE_FAILED,
    ERROR_INVALID_PORT,
    ERROR_PORT_IN_USE,
    ERROR_UNKNOWN,
    STEP_DSS_CONNECT,
    STEP_USER,
    STEP_VDC_INIT,
    STEP_ZEROCONF_SETUP,
)
from .errors import (
    CannotConnect,
    DSSHandshakeFailed,
    InvalidPort,
    PortInUse,
)

_LOGGER = logging.getLogger(__name__)


def generate_dsuid_from_ip(ip_address: str) -> str:
    """Generate deterministic dsUID from IP address."""
    # Import here to avoid circular dependency
    from pyvdcapi.core.dsuid import DSUIDGenerator
    
    # Convert IP to a pseudo-MAC format for dsUID generation
    # This ensures uniqueness while being deterministic
    ip_parts = ip_address.split('.')
    if len(ip_parts) != 4:
        raise ValueError("Invalid IP address format")
    
    # Create pseudo MAC: 02:HA:XX:XX:XX:XX where XX are IP octets
    pseudo_mac = f"02:HA:{ip_parts[0]:02x}:{ip_parts[1]:02x}:{ip_parts[2]:02x}:{ip_parts[3]:02x}"
    
    return DSUIDGenerator.generate_vdc_host_dsuid(pseudo_mac, vendor_id="HomeAssistant")


def get_local_ip() -> str:
    """Get the local IP address of the Home Assistant host."""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", port))
            return True
    except OSError:
        return False


class DigitalStromVDCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for digitalSTROM VDC."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._config: dict[str, Any] = {}
        self._local_ip: str | None = None
        self._dsuid: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - port configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            port = user_input[CONF_PORT]

            # Validate port
            if not (1024 <= port <= 65535):
                errors[CONF_PORT] = ERROR_INVALID_PORT
            elif not is_port_available(port):
                errors[CONF_PORT] = ERROR_PORT_IN_USE
            else:
                # Port is valid, store and move to VDC init
                self._config[CONF_PORT] = port
                return await self.async_step_vdc_init()

        return self.async_show_form(
            step_id=STEP_USER,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                }
            ),
            errors=errors,
        )

    async def async_step_vdc_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Initialize VDC host and generate dsUID."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._config[CONF_VDC_NAME] = user_input[CONF_VDC_NAME]
            
            # Generate dsUID from IP if user accepted the suggested one
            if user_input.get("use_generated_dsuid", True):
                self._config[CONF_DSUID] = self._dsuid
            else:
                # Allow user to provide custom dsUID (advanced users)
                self._config[CONF_DSUID] = user_input.get(CONF_DSUID, self._dsuid)
            
            return await self.async_step_zeroconf_setup()

        # Get local IP and generate dsUID
        self._local_ip = await self.hass.async_add_executor_job(get_local_ip)
        
        try:
            self._dsuid = generate_dsuid_from_ip(self._local_ip)
        except Exception as err:
            _LOGGER.error("Failed to generate dsUID: %s", err)
            errors["base"] = ERROR_UNKNOWN

        if errors:
            return self.async_show_form(
                step_id=STEP_VDC_INIT,
                errors=errors,
            )

        return self.async_show_form(
            step_id=STEP_VDC_INIT,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_VDC_NAME, default=DEFAULT_VDC_NAME): cv.string,
                    vol.Optional("use_generated_dsuid", default=True): cv.boolean,
                }
            ),
            description_placeholders={
                "ip_address": self._local_ip,
                "dsuid": self._dsuid,
            },
        )

    async def async_step_zeroconf_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure service announcement via zeroconf."""
        if user_input is not None:
            self._config[CONF_ANNOUNCE_SERVICE] = user_input[CONF_ANNOUNCE_SERVICE]
            self._config[CONF_SERVICE_NAME] = user_input[CONF_SERVICE_NAME]
            
            return await self.async_step_dss_connect()

        return self.async_show_form(
            step_id=STEP_ZEROCONF_SETUP,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ANNOUNCE_SERVICE, default=DEFAULT_ANNOUNCE_SERVICE
                    ): cv.boolean,
                    vol.Required(
                        CONF_SERVICE_NAME, default=DEFAULT_SERVICE_NAME
                    ): cv.string,
                }
            ),
        )

    async def async_step_dss_connect(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Establish connection with DSS and complete setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create the config entry
            return self.async_create_entry(
                title=self._config[CONF_VDC_NAME],
                data=self._config,
            )

        # Try to verify the configuration can work
        # (In a real implementation, we might test the connection here)
        
        return self.async_show_form(
            step_id=STEP_DSS_CONNECT,
            description_placeholders={
                "vdc_name": self._config[CONF_VDC_NAME],
                "port": str(self._config[CONF_PORT]),
                "service_name": self._config[CONF_SERVICE_NAME],
            },
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DigitalStromVDCOptionsFlow:
        """Get the options flow for this handler."""
        return DigitalStromVDCOptionsFlow(config_entry)


class DigitalStromVDCOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for digitalSTROM VDC integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._device_config: dict[str, Any] = {}
        self._selected_template: str | None = None
        self._inputs: list[dict[str, Any]] = []
        self._outputs: list[dict[str, Any]] = []
        self._entity_bindings: dict[str, str] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - show device list and add device option."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add_device":
                return await self.async_step_add_device()
            
        # Get existing devices from device manager
        from homeassistant.helpers import device_registry as dr
        
        device_registry = dr.async_get(self.hass)
        devices = dr.async_entries_for_config_entry(
            device_registry, self.config_entry.entry_id
        )
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action"): vol.In({
                    "add_device": "Add New Device",
                }),
            }),
            description_placeholders={
                "device_count": str(len(devices)),
            },
        )

    async def async_step_add_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose device creation method."""
        if user_input is not None:
            method = user_input["method"]
            if method == "template":
                return await self.async_step_template_select()
            else:
                return await self.async_step_manual_device()

        return self.async_show_form(
            step_id="add_device",
            data_schema=vol.Schema({
                vol.Required("method"): vol.In({
                    "template": "Create from Template",
                    "manual": "Create Manually",
                }),
            }),
        )

    async def async_step_template_select(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select device template."""
        from .const import DATA_TEMPLATE_MANAGER, DOMAIN
        
        if user_input is not None:
            self._selected_template = user_input["template"]
            return await self.async_step_template_configure()

        # Get available templates
        data = self.hass.data[DOMAIN][self.config_entry.entry_id]
        template_manager = data[DATA_TEMPLATE_MANAGER]
        templates = template_manager.get_available_templates()
        
        # Create selection dict with template names and descriptions
        template_choices = {
            name: f"{info['name']} - {info['description']}"
            for name, info in templates.items()
        }

        return self.async_show_form(
            step_id="template_select",
            data_schema=vol.Schema({
                vol.Required("template"): vol.In(template_choices),
            }),
        )

    async def async_step_template_configure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure template parameters and entity bindings."""
        from .const import DATA_DEVICE_MANAGER, DATA_TEMPLATE_MANAGER, DOMAIN
        
        if user_input is not None:
            # Store configuration
            instance_name = user_input["instance_name"]
            
            # Extract entity bindings from user input
            bindings = {
                key.replace("entity_", ""): value
                for key, value in user_input.items()
                if key.startswith("entity_")
            }
            
            # Create device from template
            data = self.hass.data[DOMAIN][self.config_entry.entry_id]
            device_manager = data[DATA_DEVICE_MANAGER]
            
            try:
                await device_manager.create_device_from_template(
                    template_name=self._selected_template,
                    instance_name=instance_name,
                    parameters={},  # Templates have predefined parameters
                    entity_bindings=bindings,
                )
                
                return self.async_create_entry(
                    title="Device Created",
                    data={},
                )
            except Exception as err:
                _LOGGER.error("Failed to create device: %s", err)
                return self.async_abort(reason="device_creation_failed")

        # Get template info
        data = self.hass.data[DOMAIN][self.config_entry.entry_id]
        template_manager = data[DATA_TEMPLATE_MANAGER]
        template = template_manager.get_template(self._selected_template)
        bindings = template_manager.get_template_bindings(self._selected_template)
        
        # Build schema with entity selectors for required bindings
        schema_dict = {
            vol.Required("instance_name"): cv.string,
        }
        
        # Add entity selectors for each required binding
        from homeassistant.helpers import selector
        
        for binding in bindings:
            schema_dict[vol.Required(f"entity_{binding}")] = selector.EntitySelector()
        
        return self.async_show_form(
            step_id="template_configure",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "template_name": template["name"],
                "template_description": template["description"],
            },
        )

    async def async_step_manual_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure device manually - general parameters."""
        from pyvdcapi.core.constants import DSGroup
        
        if user_input is not None:
            self._device_config = {
                "name": user_input["name"],
                "primary_group": user_input["primary_group"],
            }
            return await self.async_step_add_inputs()

        # Create list of available DSGroups
        dsgroups = {
            1: "Light (Yellow)",
            2: "Blind (Grey)",
            3: "Heating (Blue)",
            4: "Audio (Cyan)",
            5: "Video (Magenta)",
            8: "Joker (Black)",
        }

        return self.async_show_form(
            step_id="manual_device",
            data_schema=vol.Schema({
                vol.Required("name"): cv.string,
                vol.Required("primary_group", default=1): vol.In(dsgroups),
            }),
        )

    async def async_step_add_inputs(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add inputs to device."""
        if user_input is not None:
            if user_input.get("add_input"):
                input_type = user_input["input_type"]
                
                # Configure the specific input type
                if input_type == "button":
                    return await self.async_step_configure_button()
                elif input_type == "binary_input":
                    return await self.async_step_configure_binary_input()
                elif input_type == "sensor":
                    return await self.async_step_configure_sensor()
            else:
                # Done adding inputs, move to outputs
                return await self.async_step_add_output()

        return self.async_show_form(
            step_id="add_inputs",
            data_schema=vol.Schema({
                vol.Required("add_input", default=False): cv.boolean,
                vol.Optional("input_type"): vol.In({
                    "button": "Button Input",
                    "binary_input": "Binary Input",
                    "sensor": "Sensor",
                }),
            }),
            description_placeholders={
                "input_count": str(len(self._inputs)),
            },
        )

    async def async_step_configure_button(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure button input."""
        from pyvdcapi.core.constants import DSButtonType
        
        if user_input is not None:
            self._inputs.append({
                "type": "button",
                "button_type": user_input["button_type"],
                "name": user_input["name"],
            })
            return await self.async_step_add_inputs()

        button_types = {
            1: "Single Button",
            2: "Two-Way Rocker",
            3: "Four-Way Rocker",
        }

        return self.async_show_form(
            step_id="configure_button",
            data_schema=vol.Schema({
                vol.Required("name"): cv.string,
                vol.Required("button_type", default=1): vol.In(button_types),
            }),
        )

    async def async_step_configure_binary_input(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure binary input."""
        if user_input is not None:
            self._inputs.append({
                "type": "binary_input",
                "input_type": user_input["input_type"],
                "name": user_input["name"],
            })
            
            # Bind to entity
            self._entity_bindings[f"binary_input_{len(self._inputs)}"] = user_input["entity_id"]
            
            return await self.async_step_add_inputs()

        from homeassistant.helpers import selector
        
        return self.async_show_form(
            step_id="configure_binary_input",
            data_schema=vol.Schema({
                vol.Required("name"): cv.string,
                vol.Required("input_type", default=1): vol.In({
                    1: "Presence/Motion",
                    2: "Light",
                    3: "Presence in Darkness",
                    4: "Twilight",
                    5: "Motion",
                    6: "Motion in Darkness",
                }),
                vol.Required("entity_id"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="binary_sensor")
                ),
            }),
        )

    async def async_step_configure_sensor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure sensor."""
        if user_input is not None:
            self._inputs.append({
                "type": "sensor",
                "sensor_type": user_input["sensor_type"],
                "name": user_input["name"],
                "min_value": user_input.get("min_value", 0.0),
                "max_value": user_input.get("max_value", 100.0),
                "unit": user_input.get("unit", ""),
            })
            
            # Bind to entity
            self._entity_bindings[f"sensor_{len(self._inputs)}"] = user_input["entity_id"]
            
            return await self.async_step_add_inputs()

        from homeassistant.helpers import selector
        
        return self.async_show_form(
            step_id="configure_sensor",
            data_schema=vol.Schema({
                vol.Required("name"): cv.string,
                vol.Required("sensor_type", default=1): vol.In({
                    1: "Temperature",
                    2: "Humidity",
                    3: "Brightness",
                    4: "Power",
                }),
                vol.Optional("min_value", default=0.0): cv.small_float,
                vol.Optional("max_value", default=100.0): cv.small_float,
                vol.Optional("unit", default=""): cv.string,
                vol.Required("entity_id"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
            }),
        )

    async def async_step_add_output(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add output channels to device."""
        if user_input is not None:
            if user_input.get("add_output"):
                return await self.async_step_add_channel()
            else:
                # Done, finalize device
                return await self.async_step_finalize_device()

        return self.async_show_form(
            step_id="add_output",
            data_schema=vol.Schema({
                vol.Required("add_output", default=False): cv.boolean,
            }),
        )

    async def async_step_add_channel(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add output channel."""
        from pyvdcapi.core.constants import DSChannelType
        
        if user_input is not None:
            channel_config = {
                "channel_type": user_input["channel_type"],
                "min_value": user_input.get("min_value", 0.0),
                "max_value": user_input.get("max_value", 100.0),
                "initial_value": user_input.get("initial_value", 0.0),
            }
            
            # Add to first output or create new
            if not self._outputs:
                self._outputs.append({"channels": [channel_config]})
            else:
                self._outputs[0]["channels"].append(channel_config)
            
            # Bind to entity
            channel_num = len(self._outputs[0]["channels"])
            self._entity_bindings[f"output_channel_{channel_num}"] = user_input["entity_id"]
            
            # Ask if more channels needed
            return await self.async_step_add_output()

        from homeassistant.helpers import selector
        
        channel_types = {
            0: "Brightness",
            1: "Hue",
            2: "Saturation",
            3: "Color Temperature",
        }

        return self.async_show_form(
            step_id="add_channel",
            data_schema=vol.Schema({
                vol.Required("channel_type", default=0): vol.In(channel_types),
                vol.Optional("min_value", default=0.0): cv.small_float,
                vol.Optional("max_value", default=100.0): cv.small_float,
                vol.Optional("initial_value", default=0.0): cv.small_float,
                vol.Required("entity_id"): selector.EntitySelector(),
            }),
            description_placeholders={
                "channel_count": str(len(self._outputs[0]["channels"]) if self._outputs else 0),
            },
        )

    async def async_step_finalize_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create and announce device to DSS."""
        from .const import DATA_DEVICE_MANAGER, DOMAIN
        
        # Create device
        data = self.hass.data[DOMAIN][self.config_entry.entry_id]
        device_manager = data[DATA_DEVICE_MANAGER]
        
        try:
            await device_manager.create_device_manual(
                device_config=self._device_config,
                inputs=self._inputs,
                outputs=self._outputs,
                entity_bindings=self._entity_bindings,
            )
            
            return self.async_create_entry(
                title="Device Created",
                data={},
            )
        except Exception as err:
            _LOGGER.error("Failed to create device: %s", err)
            return self.async_abort(reason="device_creation_failed")
