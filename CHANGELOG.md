# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Development
- Additional device templates
- Enhanced scene management
- Energy monitoring integration
- Diagnostics sensor

---

## [0.1.0] - 2026-02-16

### Added

#### Core Integration
- Complete HACS-compliant integration structure
- Async-first architecture following Home Assistant best practices
- Config flow for UI-based setup (4-step initial wizard)
- Options flow for device management (11-step workflow)
- Integration manifest with proper metadata and dependencies
- Translation files (English) for all UI strings
- Comprehensive error handling and logging

#### VDC Host & Connection Management
- VDC Host Manager with full lifecycle control
- TCP server for dSS connections (configurable port)
- Zeroconf/mDNS service announcement for automatic discovery
- Connection monitoring with PING/PONG keep-alive
- Automatic reconnection with exponential backoff (max 5 attempts)
- DSS connection event callbacks (connected/disconnected)
- Graceful shutdown and cleanup

#### Device Management
- Device Manager for complete device lifecycle
- Template-based device creation (9 predefined templates):
  - Simple On/Off Light
  - Dimmable Light with Scenes
  - RGB Color Light
  - Wall Switch Single Button
  - Motorized Blinds
  - Temperature Sensor
  - Temperature & Humidity Sensor
  - Motion Sensor
  - Heating Controller
  - Philips HUE Lily Garden Spot (vendor-specific)
- Manual device creation with full control over:
  - Device parameters (name, dsUID, groups, zones)
  - Output channels (brightness, color, position, temperature)
  - Input sensors (temperature, humidity, power, etc.)
  - Binary inputs (motion, contact, occupancy)
  - Button inputs (single, short/long, multi-press)
- Device template refresh service
- Component indexing for entity binding

#### Platform Support (7 Platforms)
- **Light Platform** (183 lines)
  - Brightness control (0-100%)
  - RGB/HS color support
  - Color temperature support
  - Dynamic color mode detection
  - Scene support
  - Filtered to light-compatible devices
- **Switch Platform** (95 lines)
  - On/off control
  - State reporting
  - Scene support
- **Sensor Platform** (73 lines)
  - Continuous value sensors
  - Temperature, humidity, power, etc.
  - Unit conversion
  - Device class assignment
  - Platform filtering
- **Binary Sensor Platform** (72 lines)
  - Discrete state sensors
  - Motion, contact, occupancy detection
  - Device class assignment
  - Platform filtering
- **Cover Platform** (142 lines)
  - Position control (0-100%)
  - Open/close/stop commands
  - Tilt support (if available)
  - Filtered to DSGroup.BLIND (4) devices
- **Climate Platform** (115 lines)
  - Temperature setpoint control
  - Current temperature reporting
  - HVAC mode support
  - Filtered to DSGroup.HEATING (9) devices
- **Button Platform** (82 lines)
  - Button press events
  - Event firing to HA event bus
  - Support for single, short/long, multi-press
  - Platform filtering

#### Entity Binding System (256 lines)
- Bidirectional HA ↔ VDC state synchronization
- HA → VDC control binding via state listeners
- VDC → HA state reporting via callbacks
- State conversion (HA brightness 0-255 ↔ VDC 0-100%)
- Support for:
  - Output channels (lights, covers, climate)
  - Sensors (temperature, humidity, power)
  - Binary inputs (motion, contact, occupancy)
  - Button inputs (press events)
- Async locking for thread safety
- Cleanup on shutdown

#### Services (8 Custom Services)
- `digitalstrom_vdc.call_scene` - Call digitalSTROM scene
- `digitalstrom_vdc.save_scene` - Save current state as scene
- `digitalstrom_vdc.undo_scene` - Undo last scene call
- `digitalstrom_vdc.call_min_scene` - Conditional minimum scene
- `digitalstrom_vdc.dim_channel` - Incremental channel dimming
- `digitalstrom_vdc.set_local_priority` - Set scene priority
- `digitalstrom_vdc.announce_device` - Manual device announcement
- `digitalstrom_vdc.refresh_templates` - Reload device templates
- All services with voluptuous schema validation
- Service YAML definitions with descriptions

#### pyvdcapi Integration
- Full integration with pyvdcapi library (>=2026.1.1.0)
- VdcHost lifecycle management
- Vdc (Virtual Device Connector) creation
- VdSD (Virtual Device) management
- Output channel control:
  - Brightness channels (lights, switches)
  - Position channels (covers)
  - Temperature channels (climate)
  - RGB/HS color channels
- Input component handling:
  - Sensor value callbacks
  - Binary input state callbacks
  - Button press callbacks
- Scene operations (call, save, undo, min)
- Device announcement protocol
- Connection state management

#### Testing Infrastructure
- Comprehensive test suite (1,062 lines of test code)
- 50+ test cases covering:
  - Config flow (6 tests)
  - VDC manager (6 tests)
  - Device manager (8 tests)
  - Platforms (8 tests across all platforms)
  - Entity binding (10 tests)
  - Integration workflows (7 tests)
- pytest configuration with coverage reporting
- pytest-homeassistant-custom-component integration
- Mock fixtures for all VDC components
- GitHub Actions CI/CD workflow
- Linting (ruff), formatting (black), type checking (mypy)
- Codecov integration for coverage reporting

#### Documentation
- Comprehensive README with badges and quick start
- INSTALLATION.md with detailed setup instructions
- CONTRIBUTING.md with development guidelines
- DEVICE_TEMPLATES.md with template reference
- TROUBLESHOOTING.md with common issues and solutions
- ARCHITECTURE.md with technical details
- CHANGELOG.md (this file)
- Code documentation with docstrings

#### Development Tools
- GitHub Actions workflows:
  - Testing workflow (Python 3.11, 3.12)
  - HACS validation
  - hassfest validation
  - Linting and formatting checks
- Pre-commit hooks configuration
- Development dependencies in requirements_dev.txt
- pyproject.toml with tool configurations
- pytest.ini for test configuration

### Technical Details

**Total Lines of Code:**
- Production code: 2,936 lines (16 Python files)
- Test code: 1,062 lines (8 test files)
- Documentation: 1,500+ lines (8 documentation files)
- **Total: 5,500+ lines**

**Dependencies:**
- Home Assistant >=2024.1.0
- pyvdcapi >=2026.1.1.0
- protobuf >=4.0
- zeroconf (via HA core)

**Supported Home Assistant Versions:**
- 2024.1.0 and newer

**Python Version:**
- Python 3.11+

**Integration Type:**
- Hub integration with local push IoT class

**Platforms:**
- 7 platforms (light, switch, sensor, binary_sensor, cover, climate, button)

**HACS Compliance:**
- Fully HACS compliant from inception
- Follows HACS repository structure
- Includes hacs.json metadata
- Proper manifest.json configuration

### Known Limitations

- VDC-API uses unencrypted TCP (local network recommended)
- No authentication in VDC-API protocol (by design)
- Single dSS connection per integration instance
- Template-based devices limited to predefined templates (manual creation available)
- No energy monitoring in initial release
- No diagnostics sensor in initial release

### Migration Notes

This is the initial release. No migration required.

### Acknowledgments

- Built on **pyvdcapi** library by [@KarlKiel](https://github.com/KarlKiel)
- Follows digitalSTROM VDC-API specification
- Inspired by Home Assistant integration best practices

---

[Unreleased]: https://github.com/KarlKiel/HA-digitalStromVDC/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/KarlKiel/HA-digitalStromVDC/releases/tag/v0.1.0
