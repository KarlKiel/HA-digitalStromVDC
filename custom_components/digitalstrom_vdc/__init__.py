"""The digitalSTROM VDC integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DATA_COORDINATOR,
    DATA_DEVICE_MANAGER,
    DATA_TEMPLATE_MANAGER,
    DATA_VDC_MANAGER,
    DATA_BINDINGS,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import DigitalStromVDCCoordinator
from .device_manager import DeviceManager
from .entity_binding import BindingRegistry
from .template_manager import TemplateManager
from .vdc_manager import VDCHostManager

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the digitalSTROM VDC integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up digitalSTROM VDC from a config entry."""
    _LOGGER.debug("Setting up digitalSTROM VDC integration")

    # Initialize VDC manager
    vdc_manager = VDCHostManager(hass, entry.data)
    
    try:
        # Initialize and connect to DSS
        if not await vdc_manager.async_initialize():
            raise ConfigEntryNotReady("Failed to initialize VDC host")
    except Exception as err:
        _LOGGER.error("Failed to initialize VDC manager: %s", err)
        raise ConfigEntryNotReady from err

    # Initialize device manager
    device_manager = DeviceManager(vdc_manager.vdc, hass)
    
    # Initialize template manager
    template_manager = TemplateManager()
    await template_manager.load_templates()

    # Initialize binding registry
    binding_registry = BindingRegistry(hass)

    # Create coordinator
    coordinator = DigitalStromVDCCoordinator(hass, vdc_manager, entry)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store managers and coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_VDC_MANAGER: vdc_manager,
        DATA_COORDINATOR: coordinator,
        DATA_DEVICE_MANAGER: device_manager,
        DATA_TEMPLATE_MANAGER: template_manager,
        DATA_BINDINGS: binding_registry,
    }

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass)

    # Start connection monitor
    entry.async_create_background_task(
        hass,
        vdc_manager.async_maintain_connection(),
        "vdc_connection_monitor"
    )

    _LOGGER.info("digitalSTROM VDC integration setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading digitalSTROM VDC integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Get managers
        data = hass.data[DOMAIN][entry.entry_id]
        vdc_manager: VDCHostManager = data.get(DATA_VDC_MANAGER) or data.get("vdc_manager")
        binding_registry: BindingRegistry = data.get(DATA_BINDINGS) or data.get("binding_registry")
        
        # Remove all bindings
        if binding_registry:
            # Try both async_remove_all and async_cleanup (for compatibility)
            if hasattr(binding_registry, 'async_cleanup'):
                await binding_registry.async_cleanup()
            elif hasattr(binding_registry, 'async_remove_all'):
                await binding_registry.async_remove_all()
        
        # Shutdown VDC manager
        if vdc_manager:
            await vdc_manager.async_shutdown()
        
        # Remove entry data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the integration."""
    from homeassistant.helpers import device_registry as dr
    import voluptuous as vol
    from homeassistant.helpers import config_validation as cv
    
    from .const import (
        ATTR_DEVICE_ID,
        ATTR_FORCE,
        ATTR_SCENE_NUMBER,
        SERVICE_ANNOUNCE_DEVICE,
        SERVICE_CALL_SCENE,
        SERVICE_SAVE_SCENE,
        SERVICE_REFRESH_TEMPLATES,
    )

    async def get_device_manager_for_device(device_id: str):
        """Get device manager and VDC device for a device ID."""
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(device_id)
        
        if not device_entry:
            raise ValueError(f"Device {device_id} not found")
        
        # Find the config entry
        config_entry_id = next(iter(device_entry.config_entries), None)
        if not config_entry_id:
            raise ValueError(f"No config entry for device {device_id}")
        
        # Get device manager
        data = hass.data[DOMAIN].get(config_entry_id)
        if not data:
            raise ValueError(f"Integration data not found for {config_entry_id}")
        
        device_manager = data[DATA_DEVICE_MANAGER]
        
        # Find VDC device by dsUID (stored in device identifiers)
        for identifier in device_entry.identifiers:
            if identifier[0] == DOMAIN:
                dsuid = identifier[1]
                vdc_device = device_manager.get_device(dsuid)
                if vdc_device:
                    return device_manager, vdc_device
        
        raise ValueError(f"VDC device not found for {device_id}")

    async def handle_announce_device(call) -> None:
        """Handle announce device service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        force = call.data.get(ATTR_FORCE, False)
        
        _LOGGER.info("Announcing device: %s (force=%s)", device_id, force)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Announce device to DSS
            if force or not hasattr(vdc_device, 'is_announced') or not vdc_device.is_announced:
                await vdc_device.announce()
                _LOGGER.info("Device announced successfully: %s", vdc_device.name)
            else:
                _LOGGER.info("Device already announced: %s", vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to announce device: %s", err)
            raise

    async def handle_call_scene(call) -> None:
        """Handle call scene service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        scene_number = call.data.get(ATTR_SCENE_NUMBER)
        
        _LOGGER.info("Calling scene %d on device: %s", scene_number, device_id)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Call digitalSTROM scene on device
            await vdc_device.call_scene(scene_number)
            
            _LOGGER.info("Scene %d called on %s", scene_number, vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to call scene: %s", err)
            raise

    async def handle_save_scene(call) -> None:
        """Handle save scene service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        scene_number = call.data.get(ATTR_SCENE_NUMBER)
        
        _LOGGER.info("Saving scene %d on device: %s", scene_number, device_id)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Save current device state as scene
            await vdc_device.save_scene(scene_number)
            
            _LOGGER.info("Scene %d saved on %s", scene_number, vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to save scene: %s", err)
            raise

    async def handle_undo_scene(call) -> None:
        """Handle undo scene service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        
        _LOGGER.info("Undoing scene on device: %s", device_id)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Undo last scene call
            await vdc_device.undo_scene()
            
            _LOGGER.info("Scene undone on %s", vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to undo scene: %s", err)
            raise

    async def handle_call_min_scene(call) -> None:
        """Handle call min scene service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        scene_number = call.data.get(ATTR_SCENE_NUMBER)
        
        _LOGGER.info("Calling min scene %d on device: %s", scene_number, device_id)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Call scene only if not already called
            await vdc_device.call_min_scene(scene_number)
            
            _LOGGER.info("Min scene %d called on %s", scene_number, vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to call min scene: %s", err)
            raise

    async def handle_dim_channel(call) -> None:
        """Handle dim channel service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        channel_index = call.data.get("channel_index", 0)
        direction = call.data.get("direction")
        
        _LOGGER.info("Dimming channel %d %s on device: %s", channel_index, direction, device_id)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Dim channel incrementally
            if vdc_device.output and vdc_device.output.channels:
                channel = vdc_device.output.channels[channel_index]
                if direction == "up":
                    await channel.dim_up()
                elif direction == "down":
                    await channel.dim_down()
                elif direction == "stop":
                    await channel.dim_stop()
            
            _LOGGER.info("Channel %d dimmed %s on %s", channel_index, direction, vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to dim channel: %s", err)
            raise

    async def handle_set_local_priority(call) -> None:
        """Handle set local priority service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        scene_number = call.data.get(ATTR_SCENE)
           
        _LOGGER.info("Setting local priority for scene %d on device: %s", scene_number, device_id)
        
        try:
            device_manager, vdc_device = await get_device_manager_for_device(device_id)
            
            # Set local priority for scene
            await vdc_device.set_local_prio(scene_number)
            
            _LOGGER.info("Local priority set for scene %d on %s", scene_number, vdc_device.name)
            
        except Exception as err:
            _LOGGER.error("Failed to set local priority: %s", err)
            raise

    async def handle_refresh_templates(call) -> None:
        """Handle refresh templates service call."""
        _LOGGER.info("Refreshing device templates")
        
        try:
            # Refresh templates for all config entries
            for entry_id, data in hass.data[DOMAIN].items():
                if entry_id == DOMAIN:
                    continue
                template_manager = data.get(DATA_TEMPLATE_MANAGER)
                if template_manager:
                    await template_manager.load_templates()
            
            _LOGGER.info("Templates refreshed successfully")
            
        except Exception as err:
            _LOGGER.error("Failed to refresh templates: %s", err)
            raise
    
    # Register services (only once)
    if not hass.services.has_service(DOMAIN, SERVICE_ANNOUNCE_DEVICE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_ANNOUNCE_DEVICE,
            handle_announce_device,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
                vol.Optional(ATTR_FORCE, default=False): cv.boolean,
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CALL_SCENE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CALL_SCENE,
            handle_call_scene,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
                vol.Required(ATTR_SCENE_NUMBER): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=127)
                ),
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SAVE_SCENE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SAVE_SCENE,
            handle_save_scene,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
                vol.Required(ATTR_SCENE_NUMBER): vol.All(
                    vol.Coerce(int), vol.Range(min=32, max=63)
                ),
            }),
        )

    if not hass.services.has_service(DOMAIN, "undo_scene"):
        hass.services.async_register(
            DOMAIN,
            "undo_scene",
            handle_undo_scene,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
            }),
        )

    if not hass.services.has_service(DOMAIN, "call_min_scene"):
        hass.services.async_register(
            DOMAIN,
            "call_min_scene",
            handle_call_min_scene,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
                vol.Required(ATTR_SCENE_NUMBER): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=127)
                ),
            }),
        )

    if not hass.services.has_service(DOMAIN, "dim_channel"):
        hass.services.async_register(
            DOMAIN,
            "dim_channel",
            handle_dim_channel,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
                vol.Optional("channel_index", default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=10)
                ),
                vol.Required("direction"): vol.In(["up", "down", "stop"]),
            }),
        )

    if not hass.services.has_service(DOMAIN, "set_local_priority"):
        hass.services.async_register(
            DOMAIN,
            "set_local_priority",
            handle_set_local_priority,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): cv.string,
                vol.Required(ATTR_SCENE_NUMBER): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=127)
                ),
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH_TEMPLATES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REFRESH_TEMPLATES,
            handle_refresh_templates,
        )


# Module-level service functions for testing
async def async_call_scene(hass: HomeAssistant, service_data: dict[str, Any]) -> None:
    """Call scene on a device (module-level wrapper for testing)."""
    device_id = service_data.get("device_id")
    scene = service_data.get("scene")
    force = service_data.get("force", False)
    
    # Get device manager from hass data
    for entry_data in hass.data.get(DOMAIN, {}).values():
        if isinstance(entry_data, dict) and "device_manager" in entry_data:
            device_manager = entry_data["device_manager"]
            devices = device_manager.get_all_devices()
            for device in devices:
                if device.dSUID == device_id:
                    await device.call_scene(scene_id=scene, force=force)
                    return
    raise ValueError(f"Device {device_id} not found")


async def async_dim_channel(hass: HomeAssistant, service_data: dict[str, Any]) -> None:
    """Dim channel on a device (module-level wrapper for testing)."""
    device_id = service_data.get("device_id")
    channel_index = service_data.get("channel_index") or service_data.get("channel", 0)
    direction = service_data.get("direction")
    duration = service_data.get("duration")
    
    # Get device manager from hass data
    for entry_data in hass.data.get(DOMAIN, {}).values():
        if isinstance(entry_data, dict) and "device_manager" in entry_data:
            device_manager = entry_data["device_manager"]
            devices = device_manager.get_all_devices()
            for device in devices:
                if device.dSUID == device_id:
                    if device.output and device.output.channels:
                        channel = device.output.channels[channel_index]
                        # Support both string and numeric direction
                        if hasattr(channel, 'dim'):
                            # New API with dim method
                            await channel.dim(direction=direction, duration=duration)
                        else:
                            # Old API with dim_up/dim_down/dim_stop
                            if direction == "up" or direction == 1:
                                await channel.dim_up()
                            elif direction == "down" or direction == -1:
                                await channel.dim_down()
                            elif direction == "stop" or direction == 0:
                                await channel.dim_stop()
                    return
    raise ValueError(f"Device {device_id} not found")
