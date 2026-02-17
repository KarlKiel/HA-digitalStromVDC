"""Device manager for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from pyvdcapi.entities.vdc import Vdc
from pyvdcapi.entities.vdsd import VdSD

from homeassistant.core import HomeAssistant

from .errors import DeviceAnnounceFailed, TemplateNotFound

_LOGGER = logging.getLogger(__name__)


class DeviceManager:
    """Manage VDC device creation and lifecycle."""

    def __init__(self, vdc: Vdc, hass: HomeAssistant) -> None:
        """Initialize device manager."""
        self.vdc = vdc
        self.hass = hass
        self._devices: dict[str, VdSD] = {}
        self._entity_bindings: dict[str, Any] = {}

    async def create_device_from_template(
        self,
        template_name: str,
        instance_name: str,
        parameters: dict[str, Any],
        entity_bindings: dict[str, str],
    ) -> VdSD:
        """Create device from template."""
        _LOGGER.info("Creating device from template: %s", template_name)
        
        try:
            # Create device from template using pyvdcapi
            device = self.vdc.create_vdsd_from_template(
                template_name=template_name,
                instance_name=instance_name,
                **parameters
            )
            
            # Set up entity bindings
            for component_id, entity_id in entity_bindings.items():
                await self.setup_entity_binding(device, component_id, entity_id)
            
            # Store device
            self._devices[device.dSUID] = device
            
            _LOGGER.info("Device created successfully: %s", instance_name)
            return device
            
        except Exception as err:
            _LOGGER.error("Failed to create device from template: %s", err)
            raise DeviceAnnounceFailed from err

    async def create_device_manual(
        self,
        device_config: dict[str, Any],
        inputs: list[dict[str, Any]],
        outputs: list[dict[str, Any]],
        entity_bindings: dict[str, str],
    ) -> VdSD:
        """Create device manually."""
        _LOGGER.info("Creating device manually: %s", device_config.get("name"))
        
        try:
            # Create base device
            device = self.vdc.create_vdsd(
                name=device_config["name"],
                primary_group=device_config.get("primary_group", 1),
            )
            
            # Add inputs
            for input_config in inputs:
                await self._add_input_to_device(device, input_config)
            
            # Add outputs
            for output_config in outputs:
                await self._add_output_to_device(device, output_config)
            
            # Set up entity bindings
            for component_id, entity_id in entity_bindings.items():
                await self.setup_entity_binding(device, component_id, entity_id)
            
            # Store device
            self._devices[device.dSUID] = device
            
            _LOGGER.info("Device created successfully: %s", device_config["name"])
            return device
            
        except Exception as err:
            _LOGGER.error("Failed to create device manually: %s", err)
            raise DeviceAnnounceFailed from err

    async def _add_input_to_device(
        self, device: VdSD, input_config: dict[str, Any]
    ) -> None:
        """Add input component to device."""
        input_type = input_config["type"]
        
        if input_type == "button":
            device.add_button_input(
                button_type=input_config["button_type"],
                name=input_config.get("name", "Button"),
            )
        elif input_type == "binary_input":
            device.add_binary_input(
                input_type=input_config["input_type"],
                name=input_config.get("name", "Binary Input"),
            )
        elif input_type == "sensor":
            device.add_sensor(
                sensor_type=input_config["sensor_type"],
                min_value=input_config.get("min_value", 0.0),
                max_value=input_config.get("max_value", 100.0),
                unit=input_config.get("unit", ""),
            )

    async def _add_output_to_device(
        self, device: VdSD, output_config: dict[str, Any]
    ) -> None:
        """Add output component to device."""
        # Create output container if it doesn't exist
        output = device.create_output()
        
        # Add channels
        for channel_config in output_config.get("channels", []):
            output.add_output_channel(
                channel_type=channel_config["channel_type"],
                min_value=channel_config.get("min_value", 0.0),
                max_value=channel_config.get("max_value", 100.0),
                initial_value=channel_config.get("initial_value", 0.0),
            )

    async def setup_entity_binding(
        self,
        device: VdSD,
        component_id: str,
        entity_id: str,
    ) -> None:
        """Bind VDC component to HA entity."""
        from .const import DATA_BINDINGS, DOMAIN
        from .entity_binding import BindingType
        
        # Get binding registry
        data = self.hass.data[DOMAIN]
        # Find the config entry for this integration
        for entry_id, entry_data in data.items():
            if entry_id == DOMAIN:
                continue
            binding_registry = entry_data.get(DATA_BINDINGS)
            if binding_registry:
                # Determine binding type and component based on component_id
                if component_id.startswith("output_channel_"):
                    binding_type = BindingType.OUTPUT
                    # Get output channel from device
                    channel_num = int(component_id.split("_")[-1])
                    if device.output and channel_num < len(device.output.channels):
                        component = device.output.channels[channel_num]
                    else:
                        _LOGGER.error("Output channel %d not found on device", channel_num)
                        return
                        
                elif component_id.startswith("sensor_"):
                    binding_type = BindingType.SENSOR
                    sensor_num = int(component_id.split("_")[-1])
                    if sensor_num < len(device.sensors):
                        component = device.sensors[sensor_num]
                    else:
                        _LOGGER.error("Sensor %d not found on device", sensor_num)
                        return
                        
                elif component_id.startswith("binary_input_"):
                    binding_type = BindingType.BINARY_INPUT
                    input_num = int(component_id.split("_")[-1])
                    if input_num < len(device.binary_inputs):
                        component = device.binary_inputs[input_num]
                    else:
                        _LOGGER.error("Binary input %d not found on device", input_num)
                        return
                        
                elif component_id.startswith("button_"):
                    binding_type = BindingType.INPUT
                    button_num = int(component_id.split("_")[-1])
                    if button_num < len(device.button_inputs):
                        component = device.button_inputs[button_num]
                    else:
                        _LOGGER.error("Button %d not found on device", button_num)
                        return
                else:
                    _LOGGER.warning("Unknown component type: %s", component_id)
                    return
                
                # Add binding
                binding_id = f"{device.dSUID}_{component_id}"
                if component:  # Only add if we have actual component
                    await binding_registry.async_add_binding(
                        binding_id,
                        entity_id,
                        component,
                        binding_type,
                    )
                
                _LOGGER.debug("Set up entity binding: %s -> %s", component_id, entity_id)
                self._entity_bindings[component_id] = entity_id
                break

    def get_device(self, dsuid: str) -> VdSD | None:
        """Get device by dsUID."""
        return self._devices.get(dsuid)

    def get_all_devices(self) -> list[VdSD]:
        """Get all devices."""
        return list(self._devices.values())
