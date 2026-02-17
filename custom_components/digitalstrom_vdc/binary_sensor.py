"""Binary sensor platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up digitalSTROM VDC binary sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices with binary input components
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device has binary input components
        if hasattr(device, 'binary_inputs') and device.binary_inputs:
            # For each binary input, create a binary sensor entity
            for binary_input in device.binary_inputs:
                entities.append(
                    DigitalStromVDCBinarySensor(coordinator, device, binary_input)
                )

    async_add_entities(entities)


class DigitalStromVDCBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a digitalSTROM VDC binary sensor."""

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
        binary_input: Any,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._binary_input = binary_input
        self._attr_unique_id = f"{vdc_device.dSUID}_{binary_input.input_type}"
        self._attr_name = f"{vdc_device.name} {binary_input.name}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if self._binary_input:
            return bool(self._binary_input.state)
        return False

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
