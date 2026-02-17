"""Climate platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_DEVICE_MANAGER, DOMAIN
from .coordinator import DigitalStromVDCCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up digitalSTROM VDC climate devices from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices in heating group
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device is in heating group (DSGroup.HEATING)
        # DSGroup.HEATING = 9 in digitalSTROM
        if hasattr(device, 'primary_group') and device.primary_group == 9:
            entities.append(DigitalStromVDCClimate(coordinator, device))
        # Also check for devices with temperature control capabilities
        elif hasattr(device, 'sensors') and device.sensors:
            # Check if device has temperature sensor
            has_temp_sensor = any('temperature' in s.sensor_type.lower() 
                                for s in device.sensors if hasattr(s, 'sensor_type'))
            if has_temp_sensor and hasattr(device, 'output') and device.output:
                entities.append(DigitalStromVDCClimate(coordinator, device))

    async_add_entities(entities)


class DigitalStromVDCClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a digitalSTROM VDC climate device."""

    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._attr_unique_id = vdc_device.dSUID
        self._attr_name = vdc_device.name
        self._attr_min_temp = 5.0
        self._attr_max_temp = 30.0

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if hasattr(self._vdc_device, 'sensors') and self._vdc_device.sensors:
            # Get temperature from first sensor
            temp_sensor = next((s for s in self._vdc_device.sensors if 'temperature' in s.sensor_type.lower()), None)
            if temp_sensor:
                return float(temp_sensor.value)
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            return None
        primary_channel = self._vdc_device.output.channels[0]
        return float(primary_channel.value)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation mode."""
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            return HVACMode.OFF
        primary_channel = self._vdc_device.output.channels[0]
        if primary_channel.value > 0:
            return HVACMode.HEAT
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        _LOGGER.debug("Setting temperature for %s to %s", self.name, temperature)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set control value for temperature setpoint
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(float(temperature))
        
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug("Setting HVAC mode for %s to %s", self.name, hvac_mode)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set mode - OFF = set value to 0, HEAT = restore previous value or default
        primary_channel = self._vdc_device.output.channels[0]
        if hvac_mode == HVACMode.OFF:
            await primary_channel.set_value(0.0)
        elif hvac_mode == HVACMode.HEAT:
            await primary_channel.set_value(21.0)  # Default 21°C
        
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._vdc_device.dSUID)},
            "name": self._vdc_device.name,
            "manufacturer": "digitalSTROM VDC",
            "model": self._vdc_device.model,
            "via_device": (DOMAIN, self.coordinator.vdc_manager.host.dSUID),
        }
