# Architecture Documentation

Technical architecture documentation for the digitalSTROM VDC Integration.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Integration Lifecycle](#integration-lifecycle)
- [Threading & Concurrency](#threading--concurrency)
- [Error Handling](#error-handling)
- [Extension Points](#extension-points)

---

## Overview

The digitalSTROM VDC Integration is a Home Assistant custom component that implements the VDC-API protocol, enabling Home Assistant to function as a Virtual Device Connector (vDC) host. The integration uses the `pyvdcapi` library for protocol implementation and follows Home Assistant's async-first architecture.

### Key Design Principles

1. **Async-First**: All I/O operations are asynchronous
2. **Event-Driven**: Uses callbacks and event bus for state propagation
3. **Modular**: Separation of concerns across managers and platforms
4. **Extensible**: Template system and plugin architecture
5. **Resilient**: Graceful degradation and auto-recovery

### Technology Stack

- **Language**: Python 3.11+
- **Framework**: Home Assistant 2024.1.0+
- **Protocol Library**: pyvdcapi >=2026.1.1.0
- **Network**: asyncio TCP server, Zeroconf/mDNS
- **Data Serialization**: Protobuf (VDC-API), JSON (HA)

---

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant Core                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              digitalSTROM VDC Integration              │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │  Config Flow │  │ Coordinator  │  │   Services  │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │  │
│  │         │                 │                  │        │  │
│  │  ┌──────▼──────────────────▼──────────────────▼─────┐│  │
│  │  │              Integration Core (__init__)          ││  │
│  │  │  - Entry setup/unload                            ││  │
│  │  │  - Service registration                          ││  │
│  │  │  - Platform forwarding                           ││  │
│  │  └───┬────────────────────┬──────────────────────┬──┘│  │
│  │      │                    │                      │   │  │
│  │  ┌───▼──────────┐  ┌──────▼───────────┐  ┌──────▼────┐│  │
│  │  │ VDC Host     │  │ Device Manager   │  │ Template  ││  │
│  │  │ Manager      │  │                  │  │ Manager   ││  │
│  │  │              │  │ - Create devices │  │           ││  │
│  │  │ - TCP Server │  │ - Manage VdSD    │  │ - Load    ││  │
│  │  │ - Zeroconf   │  │ - Component link │  │   templates││  │
│  │  │ - Connection │  │                  │  │ - Validate││  │
│  │  │   monitoring │  │                  │  │   params  ││  │
│  │  └───┬──────────┘  └──────┬───────────┘  └───────────┘│  │
│  │      │                    │                            │  │
│  │  ┌───▼────────────────────▼───────────────────────┐   │  │
│  │  │           Entity Binding Registry              │   │  │
│  │  │   - HA ↔ VDC bidirectional sync               │   │  │
│  │  │   - State listeners                            │   │  │
│  │  │   - Callback registration                      │   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  │                                                        │  │
│  │  ┌──────────────────── Platforms ──────────────────┐  │  │
│  │  │ Light │ Switch │ Sensor │ Binary │ Cover │ ... │  │  │
│  │  └───────────────────────┬──────────────────────────┘  │  │
│  └──────────────────────────┼─────────────────────────────┘  │
│                             │                                │
└─────────────────────────────┼────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │     pyvdcapi       │
                    │                    │
                    │  - VdcHost         │
                    │  - Vdc             │
                    │  - VdSD (devices)  │
                    │  - Output channels │
                    │  - Sensors/Inputs  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   VDC-API Protocol │
                    │   (TCP/Protobuf)   │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ digitalSTROM dSS   │
                    │ (Smart Service)    │
                    └────────────────────┘
```

---

## Component Details

### 1. Integration Core (`__init__.py`)

**Responsibilities:**
- ConfigEntry setup and teardown
- Platform forwarding (light, switch, sensor, etc.)
- Service registration (8 services)
- Component lifecycle management

**Key Functions:**
- `async_setup_entry()`: Initialize integration instance
- `async_unload_entry()`: Cleanup on removal
- `async_setup_services()`: Register services
- Service handlers: `async_call_scene()`, `async_save_scene()`, etc.

**Data Storage:**
```python
hass.data[DOMAIN][entry.entry_id] = {
    "vdc_manager": VDCHostManager,
    "device_manager": DeviceManager,
    "template_manager": TemplateManager,
    "coordinator": DataUpdateCoordinator,
    "binding_registry": BindingRegistry,
}
```

### 2. VDC Host Manager (`vdc_manager.py`)

**Responsibilities:**
- VdcHost lifecycle management
- TCP server for dSS connections
- Zeroconf service announcement
- Connection monitoring (PING/PONG)
- Auto-reconnection with exponential backoff

**Architecture:**
```python
class VDCHostManager:
    def __init__(self, hass, config):
        self._vdc_host = None
        self._zeroconf = None
        self._monitoring_task = None
        self._connected = False
        
    async def async_initialize():
        # Create VdcHost
        # Start TCP server
        # Announce via Zeroconf
        # Start connection monitoring
        
    async def async_maintain_connection():
        # PING/PONG loop
        # Auto-reconnect on failure
        # Event callbacks
```

**Connection States:**
- `DISCONNECTED`: No active connection
- `CONNECTING`: Attempting to connect
- `CONNECTED`: Active dSS connection
- `RECONNECTING`: Recovering from disconnect

### 3. Device Manager (`device_manager.py`)

**Responsibilities:**
- Device creation from templates
- Manual device creation
- VdSD (virtual device) lifecycle
- Component mapping (outputs, sensors, inputs)
- Entity binding setup

**Device Creation Flow:**
```python
create_device_from_template(template_name, instance_name, parameters, bindings):
    1. Load template from TemplateManager
    2. Validate parameters
    3. Create VdSD via pyvdcapi
    4. Apply template configuration
    5. Setup entity bindings
    6. Return VdSD instance
```

**Component Indexing:**
- Output channels: `output_channel_0`, `output_channel_1`, ...
- Sensors: `sensor_0`, `sensor_1`, ...
- Binary inputs: `binary_input_0`, `binary_input_1`, ...
- Buttons: `button_input_0`, `button_input_1`, ...

### 4. Template Manager (`template_manager.py`)

**Responsibilities:**
- Load and validate device templates
- Provide template metadata
- Template parameter validation
- Template refresh

**Template Structure:**
```python
{
    "name": "simple_onoff_light",
    "device_type": "light",
    "primary_group": DSGroup.YELLOW,
    "outputs": [
        {
            "channels": [
                {
                    "channel_type": "brightness",
                    "min_value": 0.0,
                    "max_value": 100.0,
                }
            ]
        }
    ],
    "parameters": {
        "initial_brightness": 0.0,
    },
}
```

### 5. Coordinator (`coordinator.py`)

**Responsibilities:**
- Periodic data updates
- State refresh coordination
- Update listeners notification
- Error handling and logging

**Update Flow:**
```python
async def _async_update_data():
    # Poll VDC devices for state changes
    # Update HA entities
    # Return updated data
    # Trigger listener callbacks
```

### 6. Entity Binding Registry (`entity_binding.py`)

**Responsibilities:**
- Bidirectional HA ↔ VDC state synchronization
- HA state change listeners
- VDC callback registration
- State conversion (HA ↔ VDC formats)

**Binding Types:**
- **Output Channel Binding**: Light brightness, cover position, climate setpoint
- **Sensor Binding**: Temperature, humidity, power sensors
- **Binary Input Binding**: Motion, contact, occupancy sensors
- **Button Binding**: Button press events

**Synchronization:**

**HA → VDC (State Listeners):**
```python
async def _handle_ha_state_change(entity_id, old_state, new_state):
    # Extract HA state value
    # Convert to VDC format
    # Update VDC channel/component
    # Handle errors
```

**VDC → HA (Callbacks):**
```python
async def _on_channel_value_changed(value):
    # Convert VDC value to HA format
    # Fire state changed event
    # Update HA entity
```

### 7. Config Flow (`config_flow.py`)

**Responsibilities:**
- UI-based configuration wizard
- Port and name validation
- dsUID generation
- Options flow for device management

**Flow Steps:**

**Initial Setup:**
1. Configure TCP port
2. Set VDC name and dsUID
3. Configure Zeroconf
4. Complete setup

**Options Flow (Device Management):**
1. Choose creation method (template/manual)
2. Configure device parameters
3. Add inputs/outputs
4. Setup entity bindings
5. Complete and announce device

### 8. Platforms

Each platform implements standard Home Assistant entity patterns:

**Light Platform (`light.py`):**
- Brightness control
- RGB/HS color support
- Dynamic color mode detection
- Scene support

**Switch Platform (`switch.py`):**
- On/off control
- State reporting

**Sensor Platform (`sensor.py`):**
- Continuous value reporting
- Unit conversion
- Device class assignment

**Binary Sensor Platform (`binary_sensor.py`):**
- Discrete state reporting
- Device class assignment (motion, contact, etc.)

**Cover Platform (`cover.py`):**
- Position control
- Open/close/stop commands
- Filtered to DSGroup.BLIND devices

**Climate Platform (`climate.py`):**
- Temperature setpoint control
- Current temperature reporting
- Filtered to DSGroup.HEATING devices

**Button Platform (`button.py`):**
- Button press events
- Event firing to HA event bus

---

## Data Flow

### Device Creation Flow

```
User (UI) → Config Flow → Device Manager → pyvdcapi → VdSD created
                              ↓
                    Binding Registry ← Entity IDs
                              ↓
                    Setup callbacks (VDC → HA)
                              ↓
                    Setup listeners (HA → VDC)
                              ↓
                    VDC Manager → Announce to dSS
```

### State Update Flow (HA → VDC)

```
User turns on light in HA
    ↓
HA updates light entity state
    ↓
State change event fired
    ↓
Entity Binding Registry listener triggered
    ↓
Extract brightness from HA state (0-255)
    ↓
Convert to VDC format (0-100%)
    ↓
Call channel.set_value(vdc_brightness)
    ↓
pyvdcapi sends VDC-API command
    ↓
dSS receives state change
```

### State Update Flow (VDC → HA)

```
dSS sends channel value change
    ↓
pyvdcapi receives VDC-API message
    ↓
Channel value updated
    ↓
Callback triggered (on_value_changed)
    ↓
Entity Binding Registry callback handler
    ↓
Convert VDC value (0-100%) to HA format (0-255)
    ↓
Fire HA event (digitalstrom_vdc_channel_changed)
    ↓
Coordinator detects change
    ↓
HA entity state updated
```

### Scene Execution Flow

```
User calls digitalstrom_vdc.call_scene service
    ↓
Service handler in __init__.py
    ↓
Locate device by device_id
    ↓
Call device.call_scene(scene_id)
    ↓
pyvdcapi sends VDC-API scene command
    ↓
dSS executes scene
    ↓
dSS sends state updates
    ↓
VDC → HA callbacks update entities
```

---

## Integration Lifecycle

### Startup Sequence

1. **Config Entry Load**
   - HA calls `async_setup_entry()`
   - Validate configuration

2. **Component Initialization**
   - Create VDCHostManager
   - Create DeviceManager
   - Create TemplateManager
   - Create Coordinator
   - Create BindingRegistry

3. **VDC Host Start**
   - Initialize pyvdcapi VdcHost
   - Start TCP server on configured port
   - Announce via Zeroconf
   - Begin connection monitoring

4. **Platform Setup**
   - Forward to platform modules
   - Platform `async_setup_entry()` called
   - Entities created and added to HA

5. **Service Registration**
   - Register 8 services
   - Setup service schemas
   - Link service handlers

6. **Ready State**
   - Integration operational
   - Waiting for dSS connection

### dSS Connection Sequence

1. **dSS Discovers VDC**
   - Via Zeroconf announcement
   - Or manual configuration

2. **TCP Connection**
   - dSS connects to VDC host port
   - pyvdcapi handles handshake

3. **Device Announcement**
   - Existing VdSD devices announced
   - dSS adds devices to catalog

4. **Operational**
   - Bidirectional communication active
   - State sync enabled
   - Scene commands available

### Shutdown Sequence

1. **Unload Request**
   - User removes integration
   - HA calls `async_unload_entry()`

2. **Service Deregistration**
   - Remove all services

3. **Platform Unload**
   - Platform entities removed
   - Entity cleanup

4. **Binding Cleanup**
   - Deregister all state listeners
   - Remove VDC callbacks

5. **VDC Host Shutdown**
   - Stop connection monitoring
   - Close TCP server
   - Remove Zeroconf announcement
   - Close dSS connection

6. **Data Cleanup**
   - Remove from `hass.data`
   - Release resources

---

## Threading & Concurrency

### Async Architecture

**Event Loop:**
- All operations run on HA's main event loop
- No blocking calls in async context
- Use `asyncio.create_task()` for background tasks

**Concurrency Safety:**
```python
# Use asyncio.Lock for critical sections
self._lock = asyncio.Lock()

async def critical_operation():
    async with self._lock:
        # Atomic operation
        await self._update_state()
```

**Background Tasks:**
- Connection monitoring: `asyncio.create_task(self.async_maintain_connection())`
- Coordinator updates: Scheduled via `DataUpdateCoordinator`
- Event callbacks: Run on event loop

**Thread Safety:**
- No threading used (pure async)
- State mutations protected by locks
- Callback order guaranteed within component

---

## Error Handling

### Error Categories

1. **Network Errors**
   - Connection failures
   - Timeouts
   - Socket errors

2. **Configuration Errors**
   - Invalid parameters
   - Missing entities
   - Schema validation failures

3. **Protocol Errors**
   - VDC-API parsing errors
   - Unexpected messages
   - State inconsistencies

4. **Integration Errors**
   - Component initialization failures
   - Service call errors
   - Platform setup failures

### Error Handling Strategy

**Graceful Degradation:**
```python
try:
    await self.vdc_host.start()
except OSError as err:
    _LOGGER.error("Failed to start VDC host: %s", err)
    # Allow integration to load but mark as unavailable
    self._available = False
```

**Retry Logic:**
```python
for attempt in range(MAX_RETRIES):
    try:
        await self._attempt_reconnection()
        break
    except Exception as err:
        if attempt < MAX_RETRIES - 1:
            await asyncio.sleep(BACKOFF_FACTOR ** attempt)
        else:
            _LOGGER.error("Max retries exceeded")
```

**User Notification:**
```python
# Use persistent notifications for critical errors
await self.hass.services.async_call(
    "persistent_notification",
    "create",
    {
        "title": "digitalSTROM VDC Error",
        "message": "Connection to dSS lost",
    },
)
```

---

## Extension Points

### Adding New Platforms

1. Create platform file: `new_platform.py`
2. Implement `async_setup_entry()`
3. Create entity class extending `CoordinatorEntity`
4. Add platform to `PLATFORMS` in `const.py`
5. Update manifest.json if needed

### Adding New Templates

1. Edit `template_manager.py`
2. Add template definition to `TEMPLATES` dict
3. Define device structure, outputs, inputs
4. Test template creation

### Adding New Services

1. Define service in `services.yaml`
2. Add service handler in `__init__.py`
3. Implement service logic
4. Update documentation

### Custom State Conversions

Extend `entity_binding.py` to add custom state conversion logic:

```python
def _convert_ha_to_vdc(self, entity_id, ha_state):
    # Custom conversion logic
    if entity_id.startswith("custom_domain"):
        return self._custom_conversion(ha_state)
    return default_conversion(ha_state)
```

---

## Performance Considerations

### Optimization Techniques

1. **Batch Updates**: Group state updates where possible
2. **Lazy Loading**: Load templates on demand
3. **Caching**: Cache frequently accessed data (device lists, bindings)
4. **Efficient Polling**: Adjust coordinator interval based on device count
5. **Event Filtering**: Only process relevant state changes

### Scalability

**Tested Configurations:**
- Up to 50 devices per VDC instance
- Up to 200 entity bindings
- Update interval: 30-60 seconds recommended

**Resource Usage:**
- Memory: ~50-100 MB per instance
- CPU: <1% idle, <5% during updates
- Network: Minimal (VDC-API is lightweight)

---

## Security Considerations

### Network Security

- VDC-API uses unencrypted TCP (local network only)
- No authentication in VDC-API protocol
- **Recommendation**: Deploy on trusted network only
- **Firewall**: Restrict VDC port to local subnet

### Data Privacy

- No external connections (except optional Zeroconf)
- All data stays local
- No telemetry or analytics

### Input Validation

- All user inputs validated via voluptuous schemas
- Configuration flow validates parameters
- Service calls validate parameters
- Entity bindings verified before registration

---

## Future Architecture Enhancements

### Planned Improvements

1. **Multiple VDC Instances**: Support multiple dSS connections
2. **Device Templates from YAML**: External template definitions
3. **Advanced Scenes**: Scene composition and macros
4. **Diagnostics**: Built-in diagnostics sensor
5. **Migration Tools**: Import/export device configurations

### Extension Opportunities

- Custom component types
- Advanced binding rules (conditions, transformations)
- Scene scheduling integration
- Energy monitoring integration
- Voice assistant integration

---

## Developer Resources

### Code Structure

```
custom_components/digitalstrom_vdc/
├── __init__.py              # Integration core (419 lines)
├── config_flow.py           # Configuration UI
├── const.py                 # Constants
├── coordinator.py           # Data updates
├── vdc_manager.py           # VDC host (260 lines)
├── device_manager.py        # Device lifecycle (192 lines)
├── template_manager.py      # Templates
├── entity_binding.py        # State sync (256 lines)
├── errors.py                # Exceptions
├── light.py                 # Light platform (183 lines)
├── switch.py                # Switch platform (95 lines)
├── sensor.py                # Sensor platform (73 lines)
├── binary_sensor.py         # Binary sensor (72 lines)
├── cover.py                 # Cover platform (142 lines)
├── climate.py               # Climate platform (115 lines)
└── button.py                # Button platform (82 lines)

Total: ~2,936 lines of production code
```

### Testing

See [tests/](../tests/) for comprehensive test suite:
- Unit tests for all components
- Integration tests for workflows
- Fixtures for mocking pyvdcapi
- 50+ test cases, 1,062 test lines

### Dependencies

- **pyvdcapi**: VDC-API protocol implementation
- **protobuf**: Protocol Buffers for VDC-API
- **zeroconf**: Service discovery
- **voluptuous**: Schema validation

---

**Last Updated**: February 16, 2026  
**Integration Version**: 0.1.0  
**Architecture Version**: 1.0
