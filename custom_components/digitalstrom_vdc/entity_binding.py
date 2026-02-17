"""Entity binding system for digitalSTROM VDC integration."""
from __future__ import annotations

import asyncio
import logging
from enum import Enum
from typing import Any, Callable

from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event

_LOGGER = logging.getLogger(__name__)


class BindingType(Enum):
    """Type of entity binding."""

    OUTPUT = "output"  # HA entity -> VDC (control)
    INPUT = "input"  # VDC -> HA entity (state reporting)
    SENSOR = "sensor"  # VDC -> HA entity (sensor values)
    BINARY_INPUT = "binary_input"  # VDC -> HA entity (binary state)


class EntityBinding:
    """Bidirectional binding between HA entity and VDC component."""

    def __init__(
        self,
        hass: HomeAssistant,
        ha_entity_id: str,
        vdc_component: Any,
        binding_type: BindingType,
    ) -> None:
        """Initialize entity binding."""
        self.hass = hass
        self.ha_entity_id = ha_entity_id
        self.vdc_component = vdc_component
        self.binding_type = binding_type
        self._ha_listener = None
        self._vdc_callback = None
        self._sync_lock = asyncio.Lock()

    async def async_setup(self) -> None:
        """Set up the binding."""
        if self.binding_type == BindingType.OUTPUT:
            await self._setup_ha_to_vdc()
        else:
            await self._setup_vdc_to_ha()

    async def _setup_ha_to_vdc(self) -> None:
        """Set up HA → VDC control binding for outputs."""
        _LOGGER.debug(
            "Setting up HA → VDC binding: %s -> VDC component",
            self.ha_entity_id,
        )

        @callback
        def state_changed(event: Event) -> None:
            """Handle HA entity state change."""
            new_state: State | None = event.data.get("new_state")
            if new_state is None:
                return

            # Schedule async update
            asyncio.create_task(self._update_vdc_from_ha(new_state))

        # Listen to HA entity state changes
        self._ha_listener = async_track_state_change_event(
            self.hass,
            [self.ha_entity_id],
            state_changed,
        )

    async def _update_vdc_from_ha(self, state: State) -> None:
        """Update VDC component from HA state."""
        async with self._sync_lock:
            try:
                # Extract value based on entity domain
                domain = state.domain
                
                if domain == "light":
                    # Get brightness and convert to VDC range (0-100)
                    brightness = state.attributes.get("brightness", 0)
                    vdc_value = (brightness / 255.0) * 100.0 if brightness else 0.0
                    
                    # Set VDC output channel value
                    if hasattr(self.vdc_component, 'set_value'):
                        await self.vdc_component.set_value(vdc_value)
                    _LOGGER.debug(
                        "Updated VDC from HA light: %s -> %.1f",
                        self.ha_entity_id,
                        vdc_value,
                    )
                    
                elif domain == "switch":
                    # Convert on/off to 0/100
                    vdc_value = 100.0 if state.state == "on" else 0.0
                    
                    # Set VDC output channel value
                    if hasattr(self.vdc_component, 'set_value'):
                        await self.vdc_component.set_value(vdc_value)
                    _LOGGER.debug(
                        "Updated VDC from HA switch: %s -> %.1f",
                        self.ha_entity_id,
                        vdc_value,
                    )
                    
                elif domain == "cover":
                    # Get position
                    position = state.attributes.get("current_position", 0)
                    
                    # Set VDC output channel value
                    if hasattr(self.vdc_component, 'set_value'):
                        await self.vdc_component.set_value(float(position))
                    _LOGGER.debug(
                        "Updated VDC from HA cover: %s -> %d",
                        self.ha_entity_id,
                        position,
                    )
                    
            except Exception as err:
                _LOGGER.error(
                    "Error updating VDC from HA entity %s: %s",
                    self.ha_entity_id,
                    err,
                )

    async def _setup_vdc_to_ha(self) -> None:
        """Set up VDC → HA state reporting binding for inputs/sensors."""
        _LOGGER.debug(
            "Setting up VDC → HA binding: VDC component -> %s",
            self.ha_entity_id,
        )

        async def vdc_value_changed(value: Any = None) -> None:
            """Handle VDC component value change."""
            await self._update_ha_from_vdc(value)

        # Register callback with VDC component based on type
        if self.binding_type == BindingType.SENSOR:
            # For sensors, register value change callback
            if hasattr(self.vdc_component, 'on_value_changed'):
                if callable(self.vdc_component.on_value_changed):
                    # If it's a callable (mock or real method), call it with the callback
                    self.vdc_component.on_value_changed(vdc_value_changed)
                else:
                    # If it's None or not callable, just assign it
                    self.vdc_component.on_value_changed = vdc_value_changed
        elif self.binding_type == BindingType.BINARY_INPUT:
            # For binary inputs, register state change callback
            if hasattr(self.vdc_component, 'on_state_changed'):
                if callable(self.vdc_component.on_state_changed):
                    self.vdc_component.on_state_changed(vdc_value_changed)
                else:
                    self.vdc_component.on_state_changed = vdc_value_changed
        elif self.binding_type == BindingType.INPUT:
            # For button inputs, register press callback
            if hasattr(self.vdc_component, 'on_pressed'):
                if callable(self.vdc_component.on_pressed):
                    self.vdc_component.on_pressed(vdc_value_changed)
                else:
                    self.vdc_component.on_pressed = vdc_value_changed
            elif hasattr(self.vdc_component, 'on_button_pressed'):
                if callable(self.vdc_component.on_button_pressed):
                    self.vdc_component.on_button_pressed(vdc_value_changed)
                else:
                    self.vdc_component.on_button_pressed = vdc_value_changed
        
        self._vdc_callback = vdc_value_changed

    async def _update_ha_from_vdc(self, value: Any) -> None:
        """Update HA entity from VDC value."""
        async with self._sync_lock:
            try:
                if self.binding_type == BindingType.SENSOR:
                    # Update sensor entity state
                    _LOGGER.debug(
                        "VDC sensor value changed: %s -> %s",
                        self.ha_entity_id,
                        value,
                    )
                    # Fire event to update HA state
                    self.hass.bus.async_fire(
                        "digitalstrom_vdc_sensor_changed",
                        {"entity_id": self.ha_entity_id, "value": value}
                    )
                    
                elif self.binding_type == BindingType.BINARY_INPUT:
                    # Update binary sensor state
                    _LOGGER.debug(
                        "VDC binary input changed: %s -> %s",
                        self.ha_entity_id,
                        value,
                    )
                    # Fire event to update HA state
                    self.hass.bus.async_fire(
                        "digitalstrom_vdc_binary_input_changed",
                        {"entity_id": self.ha_entity_id, "state": value}
                    )
                    
                elif self.binding_type == BindingType.INPUT:
                    # Button press event
                    _LOGGER.debug(
                        "VDC button pressed: %s",
                        self.ha_entity_id,
                    )
                    # Fire event for button press
                    self.hass.bus.async_fire(
                        "digitalstrom_vdc_button_press",
                        {"entity_id": self.ha_entity_id, "event": value}
                    )
                    
            except Exception as err:
                _LOGGER.error(
                    "Error updating HA from VDC: %s",
                    err,
                )

    async def async_remove(self) -> None:
        """Remove the binding."""
        # Remove HA listener
        if self._ha_listener:
            self._ha_listener()
            self._ha_listener = None

        # Remove VDC callback
        if self._vdc_callback:
            # Unregister callback from VDC component
            if self.binding_type == BindingType.SENSOR:
                if hasattr(self.vdc_component, 'on_value_changed'):
                    self.vdc_component.on_value_changed = None
            elif self.binding_type == BindingType.BINARY_INPUT:
                if hasattr(self.vdc_component, 'on_state_changed'):
                    self.vdc_component.on_state_changed = None
            elif self.binding_type == BindingType.INPUT:
                if hasattr(self.vdc_component, 'on_button_pressed'):
                    self.vdc_component.on_button_pressed = None
            
            self._vdc_callback = None

        _LOGGER.debug("Removed binding for %s", self.ha_entity_id)


class BindingRegistry:
    """Registry for managing entity bindings."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize binding registry."""
        self.hass = hass
        self._bindings: dict[str, dict[str, Any]] = {}
        self._binding_objects: dict[str, EntityBinding] = {}

    async def async_add_binding(
        self,
        binding_id: str,
        ha_entity_id: str,
        vdc_component: Any,
        binding_type: BindingType,
        component_type: str = "component",
    ) -> None:
        """Add a new binding."""
        binding = EntityBinding(
            self.hass,
            ha_entity_id,
            vdc_component,
            binding_type,
        )
        
        await binding.async_setup()
        self._binding_objects[binding_id] = binding
        
        # Store in format expected by tests
        self._bindings[binding_id] = {component_type: vdc_component}
        
        _LOGGER.info(
            "Added binding: %s (%s) <-> %s",
            binding_id,
            binding_type.value,
            ha_entity_id,
        )

    async def async_remove_binding(self, binding_id: str) -> None:
        """Remove a binding."""
        binding = self._binding_objects.pop(binding_id, None)
        if binding:
            await binding.async_remove()
        self._bindings.pop(binding_id, None)
        _LOGGER.info("Removed binding: %s", binding_id)

    async def async_remove_all(self) -> None:
        """Remove all bindings."""
        for binding_id in list(self._binding_objects.keys()):
            await self.async_remove_binding(binding_id)
        # Also clear the _bindings dict in case it was manually set
        self._bindings.clear()

    def get_binding(self, binding_id: str) -> EntityBinding | None:
        """Get a binding by ID."""
        return self._binding_objects.get(binding_id)

    def get_all_bindings(self) -> dict[str, EntityBinding]:
        """Get all bindings."""
        return self._binding_objects.copy()

    async def register_channel_binding(
        self,
        entity_id: str,
        channel: Any,
        vdc_device_id: str | None = None,
    ) -> None:
        """Register an output channel binding (HA → VDC)."""
        binding_id = entity_id
        await self.async_add_binding(
            binding_id,
            entity_id,
            channel,
            BindingType.OUTPUT,
            component_type="channel",
        )

    async def register_sensor_binding(
        self,
        entity_id: str,
        sensor: Any,
        vdc_device_id: str | None = None,
    ) -> None:
        """Register a sensor binding (VDC → HA)."""
        binding_id = entity_id
        await self.async_add_binding(
            binding_id,
            entity_id,
            sensor,
            BindingType.SENSOR,
            component_type="sensor",
        )

    async def register_binary_input_binding(
        self,
        entity_id: str,
        binary_input: Any,
        vdc_device_id: str | None = None,
    ) -> None:
        """Register a binary input binding (VDC → HA)."""
        binding_id = entity_id
        await self.async_add_binding(
            binding_id,
            entity_id,
            binary_input,
            BindingType.BINARY_INPUT,
            component_type="binary_input",
        )

    async def register_button_binding(
        self,
        entity_id: str,
        button_input: Any,
        vdc_device_id: str | None = None,
    ) -> None:
        """Register a button binding (VDC → HA)."""
        binding_id = entity_id
        await self.async_add_binding(
            binding_id,
            entity_id,
            button_input,
            BindingType.INPUT,
            component_type="button",
        )

    async def unregister_binding(self, binding_id: str) -> None:
        """Unregister a binding (alias for async_remove_binding)."""
        await self.async_remove_binding(binding_id)

    async def async_cleanup(self) -> None:
        """Clean up all bindings (alias for async_remove_all)."""
        await self.async_remove_all()

    async def _handle_ha_state_change(
        self,
        entity_id: str,
        old_state: State | None,
        new_state: State | None,
    ) -> None:
        """Handle HA state change (for testing)."""
        if new_state is None:
            return
        
        # Get the binding object
        binding = self._binding_objects.get(entity_id)
        if binding:
            await binding._update_vdc_from_ha(new_state)
