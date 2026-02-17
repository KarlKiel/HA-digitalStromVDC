# Home Assistant digitalSTROM VDC Integration - Implementation Plan

## Executive Summary

This document outlines the complete implementation plan for a HACS-compliant, asynchronous Home Assistant integration for the digitalSTROM VDC-API. The integration leverages the `pyvdcapi` library to create a virtual device connector (vDC) host that enables Home Assistant to communicate with digitalSTROM Smart Services (dSS) via the VDC-API protocol.

**Target Timeline:** 4-6 weeks  
**HACS Compliance:** Full compliance from inception  
**Architecture:** Async-first, config flow based, follows HA best practices

---

## Phase 1: Project Foundation & Structure (Week 1)

### 1.1 Repository & Directory Structure

Create HACS-compliant folder structure:

```
custom_components/
└── digitalstrom_vdc/
    ├── __init__.py                 # Integration setup & coordinator
    ├── manifest.json               # Integration metadata
    ├── config_flow.py              # UI-based configuration flow
    ├── const.py                    # Constants and defaults
    ├── coordinator.py              # Data update coordinator
    ├── vdc_manager.py              # VDC host management
    ├── device_manager.py           # Device creation & management
    ├── template_manager.py         # Template handling
    ├── errors.py                   # Custom exceptions
    ├── services.yaml               # Service definitions
    ├── strings.json                # UI translations (en)
    ├── translations/               # Localization files
    │   └── en.json
    ├── light.py                    # Light platform
    ├── switch.py                   # Switch platform
    ├── sensor.py                   # Sensor platform
    ├── binary_sensor.py            # Binary sensor platform
    ├── cover.py                    # Cover/blinds platform
    ├── climate.py                  # Climate/heating platform
    └── button.py                   # Button platform

docs/
├── README.md                       # User documentation
├── INSTALLATION.md                 # Installation guide
└── CONTRIBUTING.md                 # Developer guide

.github/
├── workflows/
│   ├── validate.yaml               # HACS validation
│   └── release.yaml                # Release automation
└── ISSUE_TEMPLATE/
    ├── bug_report.md
    └── feature_request.md

hacs.json                           # HACS metadata
README.md                           # Main repository README
LICENSE                             # GPL-3.0 (match pyvdcapi)
```

### 1.2 Core Files Setup

#### manifest.json
```json
{
  "domain": "digitalstrom_vdc",
  "name": "digitalSTROM VDC Integration",
  "codeowners": ["@YourGitHubUsername"],
  "config_flow": true,
  "dependencies": ["zeroconf"],
  "documentation": "https://github.com/YourUsername/HA-digitalStromVDC",
  "integration_type": "hub",
  "iot_class": "local_push",
  "issue_tracker": "https://github.com/YourUsername/HA-digitalStromVDC/issues",
  "requirements": [
    "pyvdcapi>=2026.1.1.0",
    "protobuf>=4.0",
    "pyyaml>=6.0"
  ],
  "version": "0.1.0",
  "zeroconf": []
}
```

#### hacs.json
```json
{
  "name": "digitalSTROM VDC Integration",
  "render_readme": true,
  "domains": [
    "light",
    "switch",
    "sensor",
    "binary_sensor",
    "cover",
    "climate",
    "button"
  ],
  "homeassistant": "2024.1.0"
}
```

### 1.3 Development Environment

**Tasks:**
- [ ] Set up Python virtual environment (Python 3.11+)
- [ ] Install Home Assistant Core for development
- [ ] Install pyvdcapi library
- [ ] Configure development tools (black, pylint, mypy, pre-commit)
- [ ] Set up VS Code/IDE with HA integration development extensions
- [ ] Create initial Git repository with proper .gitignore

---

## Phase 2: Core Integration Implementation (Week 1-2)

### 2.1 Configuration Flow (`config_flow.py`)

Implement multi-step configuration flow:

**Step 1: Initial Setup**
- User provides TCP port number (default: 8444)
- Validate port availability
- Store in config entry

**Step 2: VDC Host Initialization**
- Auto-detect Home Assistant host IP address
- Generate deterministic dsUID from IP/MAC
- Display generated dsUID to user for confirmation
- Configure VDC name (default: "Home Assistant VDC")

**Step 3: Zeroconf Announcement**
- Configure service announcement settings
- Enable/disable auto-discovery
- Set service name

**Step 4: DSS Connection**
- Initiate handshake with DSS
- Wait for DSS acknowledgment
- Verify connection established
- Store connection state

**Implementation Details:**
```python
class DigitalStromVDCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for digitalSTROM VDC."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle initial step - port configuration."""
        
    async def async_step_vdc_init(self, user_input=None):
        """Initialize VDC host and generate dsUID."""
        
    async def async_step_zeroconf_setup(self, user_input=None):
        """Configure service announcement."""
        
    async def async_step_dss_connect(self, user_input=None):
        """Establish connection with DSS."""
```

### 2.2 Integration Core (`__init__.py`)

**Responsibilities:**
- Initialize VDC host on setup
- Set up coordinator
- Forward setup to platforms
- Handle entry reload/unload
- Manage connection lifecycle

**Key Functions:**
```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up digitalSTROM VDC from a config entry."""
    # 1. Initialize VDC host with stored config
    # 2. Start TCP server
    # 3. Announce service via zeroconf
    # 4. Establish DSS connection
    # 5. Create coordinator
    # 6. Forward to platforms
    # 7. Register services
    
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # 1. Unload platforms
    # 2. Stop coordinator
    # 3. Disconnect from DSS gracefully
    # 4. Stop TCP server
    # 5. Remove zeroconf announcement
```

### 2.3 VDC Manager (`vdc_manager.py`)

Wrapper around pyvdcapi VdcHost:

```python
class VDCHostManager:
    """Manage the VDC host and connection to DSS."""
    
    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize VDC manager."""
        self.hass = hass
        self._host: VdcHost = None
        self._config = config
        self._vdc: Vdc = None
        self._connection_state = ConnectionState.DISCONNECTED
        
    async def async_initialize(self) -> bool:
        """Initialize VDC host and establish connection."""
        # 1. Create VdcHost instance
        # 2. Create primary Vdc
        # 3. Start TCP server
        # 4. Announce via zeroconf (using zeroconf library, not avahi)
        # 5. Wait for DSS connection
        # 6. Perform handshake
        # 7. Announce VDC
        
    async def async_maintain_connection(self):
        """Keep connection alive with DSS."""
        # Periodic ping/pong
        # Reconnect on disconnect
        # Update connection state
        
    async def async_shutdown(self):
        """Gracefully shutdown VDC host."""
        # Send BYE message
        # Stop server
        # Remove zeroconf service
```

### 2.4 Coordinator (`coordinator.py`)

```python
class DigitalStromVDCCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates from VDC devices."""
    
    def __init__(self, hass: HomeAssistant, vdc_manager: VDCHostManager):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.vdc_manager = vdc_manager
        
    async def _async_update_data(self):
        """Fetch data from VDC."""
        # Query device states
        # Update internal state cache
        # Return updated data
```

---

## Phase 3: Device Management UI (Week 2-3)

### 3.1 Device Options Flow

Implement "Add Device" button using options flow:

```python
class DigitalStromVDCOptionsFlow(config_entries.OptionsFlow):
    """Handle device addition and management."""
    
    async def async_step_init(self, user_input=None):
        """Manage devices."""
        # Show list of existing devices
        # Option to add new device
        
    async def async_step_add_device(self, user_input=None):
        """Choose device creation method."""
        # Option 1: Create from template
        # Option 2: Create manually
        
    async def async_step_template_select(self, user_input=None):
        """Select device template."""
        # List available templates from pyvdcapi
        # deviceType templates (simple_onoff_light, etc.)
        # vendorType templates (philips_hue_lily, etc.)
        
    async def async_step_template_configure(self, user_input=None):
        """Configure template parameters."""
        # Based on selected template
        # Request required parameters
        # Select HA entities for data binding
        
    async def async_step_manual_device(self, user_input=None):
        """Configure device manually - general parameters."""
        # Device name
        # Primary group (DSGroup)
        # Zone assignment
        # Model info
        
    async def async_step_add_inputs(self, user_input=None):
        """Add inputs to device."""
        # Add button inputs
        # Add binary inputs
        # Add sensors
        # Select source HA entities
        
    async def async_step_add_output(self, user_input=None):
        """Add output channels to device."""
        # Add first output (creates output container)
        # Channel type selection
        # Min/max values
        # Select target HA entity
        
    async def async_step_add_channel(self, user_input=None):
        """Add additional output channels."""
        # For multi-channel devices (RGB, RGBW, etc.)
        
    async def async_step_finalize_device(self, user_input=None):
        """Create and announce device to DSS."""
```

### 3.2 Device Manager (`device_manager.py`)

```python
class DeviceManager:
    """Manage VDC device creation and lifecycle."""
    
    def __init__(self, vdc: Vdc, hass: HomeAssistant):
        """Initialize device manager."""
        self.vdc = vdc
        self.hass = hass
        self._devices: dict[str, VdSD] = {}
        self._entity_bindings: dict[str, EntityBinding] = {}
        
    async def create_device_from_template(
        self,
        template_name: str,
        instance_name: str,
        parameters: dict,
        entity_bindings: dict
    ) -> VdSD:
        """Create device from template."""
        # 1. Load template from pyvdcapi
        # 2. Apply parameters
        # 3. Create device instance
        # 4. Set up entity bindings
        # 5. Announce to DSS
        # 6. Register callbacks
        
    async def create_device_manual(
        self,
        device_config: dict,
        inputs: list,
        outputs: list,
        entity_bindings: dict
    ) -> VdSD:
        """Create device manually."""
        # 1. Create VdSD with basic parameters
        # 2. Add inputs (buttons, binary inputs, sensors)
        # 3. Create output container if needed
        # 4. Add output channels
        # 5. Set up entity bindings
        # 6. Announce to DSS
        # 7. Register callbacks
        
    async def setup_entity_binding(
        self,
        vdc_device: VdSD,
        component: Any,  # OutputChannel, Sensor, BinaryInput, etc.
        ha_entity_id: str,
        binding_type: BindingType
    ):
        """Bind VDC component to HA entity."""
        # For outputs: HA entity -> VDC (control)
        # For inputs: VDC -> HA entity (state reporting)
```

### 3.3 Template Manager (`template_manager.py`)

```python
class TemplateManager:
    """Manage device templates from pyvdcapi."""
    
    def __init__(self):
        """Initialize template manager."""
        self._available_templates: dict[str, dict] = {}
        
    async def load_templates(self):
        """Load available templates from pyvdcapi."""
        # Scan pyvdcapi/templates/
        # Parse template descriptions
        # Build UI-friendly template list
        
    def get_template_parameters(self, template_name: str) -> list:
        """Get required parameters for template."""
        # Parse TEMPLATE_DESCRIPTION_FIELD
        # Return list of required parameters
        
    def get_template_bindings(self, template_name: str) -> list:
        """Get required entity bindings for template."""
        # Determine which HA entities needed
        # Return binding requirements
```

---

## Phase 4: Platform Implementation (Week 3-4)

### 4.1 Light Platform (`light.py`)

Support devices with brightness/color outputs:

```python
class DigitalStromVDCLight(CoordinatorEntity, LightEntity):
    """Representation of a digitalSTROM VDC light."""
    
    def __init__(self, coordinator, vdc_device: VdSD, output_channel):
        """Initialize light."""
        
    @property
    def brightness(self) -> int | None:
        """Return brightness."""
        
    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return RGB color."""
        
    async def async_turn_on(self, **kwargs):
        """Turn on light."""
        # Update output channel value
        # Push to DSS
        
    async def async_turn_off(self, **kwargs):
        """Turn off light."""
```

### 4.2 Switch Platform (`switch.py`)

For on/off devices:

```python
class DigitalStromVDCSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a digitalSTROM VDC switch."""
```

### 4.3 Sensor Platform (`sensor.py`)

For continuous value sensors:

```python
class DigitalStromVDCSensor(CoordinatorEntity, SensorEntity):
    """Representation of a digitalSTROM VDC sensor."""
    
    # Temperature, humidity, power, etc.
    # Bound to VDC sensor components
```

### 4.4 Binary Sensor Platform (`binary_sensor.py`)

For discrete state sensors:

```python
class DigitalStromVDCBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a digitalSTROM VDC binary sensor."""
    
    # Motion, contact, occupancy, etc.
    # Bound to VDC binary input components
```

### 4.5 Cover Platform (`cover.py`)

For blinds/shades:

```python
class DigitalStromVDCCover(CoordinatorEntity, CoverEntity):
    """Representation of a digitalSTROM VDC cover."""
    
    # Position control
    # Tilt control (if supported)
```

### 4.6 Climate Platform (`climate.py`)

For heating/cooling devices:

```python
class DigitalStromVDCClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a digitalSTROM VDC climate device."""
    
    # Temperature setpoint
    # Control values
    # Operating modes
```

### 4.7 Button Platform (`button.py`)

For button inputs from DSS:

```python
class DigitalStromVDCButton(CoordinatorEntity, ButtonEntity):
    """Representation of a digitalSTROM VDC button."""
    
    # Trigger HA automations on button clicks
    # Support different click types (single, double, long)
```

---

## Phase 5: Entity Binding System (Week 4)

### 5.1 Binding Architecture

Create bidirectional binding between HA entities and VDC components:

**Direction 1: HA → VDC (Control)**
- HA entity state changes trigger VDC output updates
- Use HA state change listeners
- Update VDC output channels
- Push notifications to DSS

**Direction 2: VDC → HA (State Reporting)**
- VDC input changes update HA entities
- Use pyvdcapi callbacks
- Fire HA events
- Update entity states

```python
class EntityBinding:
    """Bidirectional binding between HA entity and VDC component."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        ha_entity_id: str,
        vdc_component: Any,
        binding_type: BindingType
    ):
        """Initialize binding."""
        
    async def setup_ha_to_vdc(self):
        """Set up HA → VDC control binding."""
        # Listen to HA entity state changes
        # Update VDC component on change
        
    async def setup_vdc_to_ha(self):
        """Set up VDC → HA state reporting."""
        # Register VDC callback
        # Update HA entity on VDC change
        # Fire HA events
```

### 5.2 State Synchronization

```python
class StateSynchronizer:
    """Keep HA and VDC states synchronized."""
    
    async def sync_output_to_ha(self, vdc_output, ha_entity_id):
        """Sync VDC output state to HA entity."""
        
    async def sync_input_from_ha(self, ha_entity_id, vdc_input):
        """Sync HA entity state to VDC input."""
```

---

## Phase 6: Services & Advanced Features (Week 5)

### 6.1 Custom Services

Define services in `services.yaml`:

```yaml
announce_device:
  name: Announce Device
  description: Manually announce device to DSS
  target:
    device:
      integration: digitalstrom_vdc
  fields:
    force:
      name: Force Announcement
      description: Force re-announcement even if already announced
      selector:
        boolean:

call_scene:
  name: Call Scene
  description: Call a digitalSTROM scene on a device
  target:
    device:
      integration: digitalstrom_vdc
  fields:
    scene_number:
      name: Scene Number
      description: Scene number (0-127)
      required: true
      selector:
        number:
          min: 0
          max: 127

save_scene:
  name: Save Scene
  description: Save current device state as a scene
  target:
    device:
      integration: digitalstrom_vdc
  fields:
    scene_number:
      name: Scene Number
      description: Scene number (32-63 for user scenes)
      required: true
      selector:
        number:
          min: 32
          max: 63

refresh_templates:
  name: Refresh Templates
  description: Reload available device templates
```

### 6.2 Service Implementation

```python
async def async_setup_services(hass: HomeAssistant):
    """Set up services for the integration."""
    
    async def handle_announce_device(call):
        """Handle announce device service call."""
        
    async def handle_call_scene(call):
        """Handle call scene service call."""
        
    async def handle_save_scene(call):
        """Handle save scene service call."""
        
    async def handle_refresh_templates(call):
        """Handle refresh templates service call."""
    
    # Register services
    hass.services.async_register(DOMAIN, "announce_device", handle_announce_device)
    hass.services.async_register(DOMAIN, "call_scene", handle_call_scene)
    hass.services.async_register(DOMAIN, "save_scene", handle_save_scene)
    hass.services.async_register(DOMAIN, "refresh_templates", handle_refresh_templates)
```

### 6.3 Connection Monitoring

```python
class ConnectionMonitor:
    """Monitor and maintain DSS connection."""
    
    def __init__(self, vdc_manager: VDCHostManager):
        """Initialize monitor."""
        
    async def monitor_connection(self):
        """Continuously monitor connection health."""
        # Periodic PING
        # Detect disconnections
        # Attempt reconnection
        # Update connection state
        # Fire HA events on state change
```

---

## Phase 7: Testing & Quality Assurance (Week 5-6)

### 7.1 Unit Tests

Create comprehensive test suite:

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_config_flow.py         # Config flow tests
├── test_vdc_manager.py         # VDC manager tests
├── test_device_manager.py      # Device manager tests
├── test_template_manager.py    # Template manager tests
├── test_entity_bindings.py     # Binding tests
├── test_platforms/
│   ├── test_light.py
│   ├── test_switch.py
│   ├── test_sensor.py
│   ├── test_binary_sensor.py
│   ├── test_cover.py
│   ├── test_climate.py
│   └── test_button.py
└── test_services.py            # Service tests
```

### 7.2 Integration Tests

Test with actual DSS simulator:
- Use pyvdcapi's vdSM simulator
- Test full message flow
- Verify scene operations
- Test connection recovery

### 7.3 HACS Validation

Ensure HACS compliance:
- [ ] Run HACS validation action
- [ ] Verify manifest.json structure
- [ ] Check hacs.json validity
- [ ] Ensure proper branding (no Home Assistant logos)
- [ ] Validate README structure
- [ ] Check for required documentation

---

## Phase 8: Documentation & Release (Week 6)

### 8.1 User Documentation

**README.md:**
- Overview and features
- Installation instructions (manual & HACS)
- Configuration guide
- Device setup examples
- Troubleshooting

**INSTALLATION.md:**
- Detailed installation steps
- Prerequisites
- DSS configuration requirements
- Network setup
- Port forwarding if needed

**docs/DEVICE_TEMPLATES.md:**
- Available templates
- Template parameter descriptions
- Entity binding requirements
- Custom template creation

**docs/TROUBLESHOOTING.md:**
- Common issues and solutions
- Debug logging setup
- Connection problems
- DSS handshake failures

### 8.2 Developer Documentation

**CONTRIBUTING.md:**
- Development setup
- Code style guide
- Testing requirements
- Pull request process

**ARCHITECTURE.md:**
- System architecture
- Component interactions
- Data flow diagrams
- Extension points

### 8.3 Release Preparation

- [ ] Version tagging
- [ ] Changelog generation
- [ ] GitHub release creation
- [ ] HACS default repository submission
- [ ] Community forum announcement

---

## Implementation Priorities & Dependencies

### Critical Path
1. **Phase 2.1-2.3:** Core integration & VDC manager (foundation for everything)
2. **Phase 3.2:** Device manager (needed before platforms)
3. **Phase 4.1-4.2:** Light & Switch platforms (most common use cases)
4. **Phase 5.1:** Entity binding system (enables device operation)

### Parallel Work Opportunities
- **Phase 1** and **Phase 7.3** (structure and validation) can be done early
- **Phase 4.3-4.7:** Additional platforms can be implemented in parallel
- **Phase 6.1:** Service definitions can be written alongside platform development
- **Phase 8:** Documentation can be written incrementally

### Testing Strategy
- Write tests alongside implementation (TDD approach)
- Test each phase completion before moving forward
- Use DSS simulator for integration tests
- Manual testing with actual DSS instance in Week 6

---

## Technical Considerations

### Async Best Practices
- All I/O operations use `async`/`await`
- No blocking calls in event loop
- Proper exception handling in async contexts
- Use `asyncio.create_task()` for background tasks

### Error Handling
- Graceful degradation on DSS disconnect
- User-friendly error messages in UI
- Comprehensive logging at appropriate levels
- Recovery mechanisms for transient failures

### Performance
- Minimize DSS round trips
- Cache device states locally
- Batch property updates when possible
- Use coordinator for efficient updates

### Security
- Validate all user inputs
- Sanitize device names and parameters
- Rate limiting for DSS commands
- Secure storage of configuration

### HACS Compliance Checklist
- [x] `manifest.json` with required fields
- [x] `hacs.json` configuration
- [x] Clear README with badges
- [x] Proper versioning (semver)
- [x] LICENSE file
- [x] No analytics/tracking
- [x] No breaking on Home Assistant updates
- [x] Community support commitment

---

## Resource Requirements

### Development Tools
- Python 3.11+
- Home Assistant Core (dev environment)
- pyvdcapi library
- VS Code with Python & HA extensions
- Git & GitHub account
- DSS instance or simulator

### Knowledge Prerequisites
- Home Assistant integration development
- Async Python programming
- digitalSTROM VDC-API protocol
- Config flow patterns
- Zeroconf/mDNS

### External Dependencies
- `pyvdcapi>=2026.1.1.0`
- `protobuf>=4.0`
- `pyyaml>=6.0`
- Home Assistant's `zeroconf` component

---

## Success Criteria

### Phase Completion Criteria
- **Phase 1:** Project structure validated by HACS action
- **Phase 2:** Integration loads and connects to DSS
- **Phase 3:** Devices can be added via UI
- **Phase 4:** At least light and switch platforms functional
- **Phase 5:** Entity bindings work bidirectionally
- **Phase 6:** All services functional
- **Phase 7:** 80%+ test coverage, HACS validated
- **Phase 8:** Documentation complete, ready for release

### Release Criteria
- [ ] All phases complete
- [ ] Test coverage ≥ 80%
- [ ] HACS validation passing
- [ ] Manual testing with real DSS successful
- [ ] Documentation peer-reviewed
- [ ] No critical bugs open
- [ ] Performance acceptable (< 1s device response)
- [ ] Community feedback incorporated

---

## Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| pyvdcapi compatibility issues | High | Early integration testing, maintain fork if needed |
| DSS protocol changes | Medium | Version pinning, update monitoring |
| HA breaking changes | Medium | Follow HA dev updates, test with beta releases |
| Zeroconf conflicts | Low | Thorough testing, fallback to manual configuration |

### Schedule Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Underestimated complexity | Medium | Phased approach, MVP focus, defer advanced features |
| Testing delays | Low | Continuous testing, early simulator setup |
| Documentation lag | Low | Incremental documentation, dedicated time in Phase 8 |

---

## Future Enhancements (Post-Release)

### Version 0.2.0
- Advanced scene management UI
- Device groups and zones
- Bulk device import/export
- Custom template editor

### Version 0.3.0
- Diagnostics integration
- Energy monitoring support
- Advanced automation triggers
- Device statistics

### Version 1.0.0
- Full DSS feature parity
- Multi-DSS support
- Cloud backup integration
- Mobile app optimization

---

## Conclusion

This implementation plan provides a comprehensive roadmap for developing a production-ready, HACS-compliant Home Assistant integration for digitalSTROM VDC-API. The phased approach ensures steady progress with clear milestones, while maintaining flexibility for adjustments based on testing and user feedback.

**Key Success Factors:**
1. HACS compliance from day one
2. Leveraging pyvdcapi library effectively
3. User-friendly device configuration flow
4. Robust entity binding system
5. Comprehensive testing and documentation
6. Active community engagement

**Estimated Delivery:** 6 weeks for v0.1.0 release  
**Maintenance Model:** Active development, bi-weekly releases for first 3 months  
**Community Support:** GitHub issues, Home Assistant Community forum

---

*Last Updated: February 14, 2026*  
*Version: 1.0*  
*Author: Implementation Team*
