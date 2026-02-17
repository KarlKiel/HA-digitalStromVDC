"""Light platform for digitalSTROM VDC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
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
    """Set up digitalSTROM VDC lights from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DigitalStromVDCCoordinator = data[DATA_COORDINATOR]
    device_manager = data[DATA_DEVICE_MANAGER]

    # Get all devices with output channels suitable for lights
    entities = []
    for device in device_manager.get_all_devices():
        # Check if device has light-compatible outputs
        # This would be based on primary_group == DSGroup.LIGHT or output channels
        entities.append(DigitalStromVDCLight(coordinator, device))

    async_add_entities(entities)


class DigitalStromVDCLight(CoordinatorEntity, LightEntity):
    """Representation of a digitalSTROM VDC light."""

    def __init__(
        self,
        coordinator: DigitalStromVDCCoordinator,
        vdc_device: Any,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._vdc_device = vdc_device
        self._attr_unique_id = vdc_device.dSUID
        self._attr_name = vdc_device.name
        
        # Determine color modes based on output channels
        self._determine_color_modes()

    def _determine_color_modes(self) -> None:
        """Determine supported color modes from output channels."""
        # Get output channels from VDC device
        # This is a simplified version - full implementation would check actual channels
        
        # Determine supported color modes based on available channels
        if self._vdc_device.output and self._vdc_device.output.channels:
            channels = self._vdc_device.output.channels
            # Check for RGB channels (hue and saturation)
            has_hue = any(ch.channel_type == "hue" for ch in channels)
            has_saturation = any(ch.channel_type == "saturation" for ch in channels)
            # Check for color temperature channel
            has_ct = any(ch.channel_type == "colorTemperature" for ch in channels)
            
            if has_hue and has_saturation:
                self._attr_color_mode = ColorMode.HS
                self._attr_supported_color_modes = {ColorMode.HS}
            elif has_ct:
                self._attr_color_mode = ColorMode.COLOR_TEMP
                self._attr_supported_color_modes = {ColorMode.COLOR_TEMP}
            else:
                self._attr_color_mode = ColorMode.BRIGHTNESS
                self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        else:
            # Default to brightness only
            self._attr_color_mode = ColorMode.BRIGHTNESS
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        # Get brightness from VDC device output channel
        # For now, return a default
        return self._get_brightness() > 0

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        # Convert from VDC 0-100 range to HA 0-255 range
        vdc_brightness = self._get_brightness()
        if vdc_brightness is None:
            return None
        return int((vdc_brightness / 100.0) * 255)

    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the hue and saturation color value [float, float]."""
        if ColorMode.HS not in self._attr_supported_color_modes:
            return None
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            return None
            
        channels = self._vdc_device.output.channels
        hue_channel = next((ch for ch in channels if ch.channel_type == "hue"), None)
        sat_channel = next((ch for ch in channels if ch.channel_type == "saturation"), None)
        
        if hue_channel and sat_channel:
            # Convert from VDC range (0-360 for hue, 0-100 for saturation) to HA range
            hue = float(hue_channel.value)
            saturation = float(sat_channel.value)
            return (hue, saturation)
        
        return None

    def _get_brightness(self) -> float:
        """Get brightness value from VDC device."""
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            return 0.0
            
        # Get brightness from first channel (usually the brightness channel)
        primary_channel = self._vdc_device.output.channels[0]
        return float(primary_channel.value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        _LOGGER.debug("Turning on light: %s", self.name)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Extract brightness if provided
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is not None:
            # Convert HA 0-255 to VDC 0-100
            vdc_brightness = (brightness / 255.0) * 100.0
        else:
            vdc_brightness = 100.0

        # Extract color if provided
        hs_color = kwargs.get(ATTR_HS_COLOR)
        
        # Handle color if provided
        if hs_color:
            hue, saturation = hs_color
            channels = self._vdc_device.output.channels
            
            # Set hue channel
            hue_channel = next((ch for ch in channels if ch.channel_type == "hue"), None)
            if hue_channel:
                await hue_channel.set_value(hue)
            
            # Set saturation channel
            sat_channel = next((ch for ch in channels if ch.channel_type == "saturation"), None)
            if sat_channel:
                await sat_channel.set_value(saturation)
        
        # Set brightness on primary channel
        primary_channel = self._vdc_device.output.channels[0]
        await primary_channel.set_value(vdc_brightness)
        
        # Request coordinator update
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        _LOGGER.debug("Turning off light: %s", self.name)
        
        if not self._vdc_device.output or not self._vdc_device.output.channels:
            _LOGGER.error("Device %s has no output channels", self.name)
            return
        
        # Set all output channels to 0
        for channel in self._vdc_device.output.channels:
            await channel.set_value(0.0)
        
        # Request coordinator update
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
