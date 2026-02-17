"""Sensor platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up digitalSTROM VDC sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices with sensor inputs
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device has sensor components
        if hasattr(device, 'sensors') and device.sensors:
            # For each sensor, create a sensor entity
            for sensor in device.sensors:
                entities.append(
                    DigitalStromVDCSensor(coordinator, device, sensor)
                )

    async_add_entities(entities)


class DigitalStromVDCSensor(CoordinatorEntity, SensorEntity):
    """Representation of a digitalSTROM VDC sensor."""

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
        sensor_component: Any,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._sensor = sensor_component
        self._attr_unique_id = f"{vdc_device.dSUID}_{sensor_component.sensor_type}"
        self._attr_name = f"{vdc_device.name} {sensor_component.name}"
        self._attr_native_unit_of_measurement = sensor_component.unit

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self._sensor:
            return float(self._sensor.value)
        return None

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
