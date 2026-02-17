# Device Templates Guide

This document describes all available device templates and how to use them for quick device deployment in the digitalSTROM VDC Integration.

## Overview

Device templates provide pre-configured device definitions that can be quickly deployed with minimal configuration. Each template includes:

- **Device Type**: General device classification
- **Primary Group**: digitalSTROM functional group (DSGroup)
- **Output Channels**: Pre-configured channel types and ranges
- **Input Components**: Sensors, binary inputs, or buttons (if applicable)
- **Default Parameters**: Sensible defaults for quick deployment

## Available Templates

### 1. Simple On/Off Light (`simple_onoff_light`)

Basic light with brightness control (0-100%).

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: 1 brightness channel (0-100%)
- **Inputs**: None
- **Scenes**: Supports standard lighting scenes
- **Entity Binding**: Requires one `light` entity

**Configuration:**
```yaml
Template: simple_onoff_light
Instance Name: Living Room Ceiling Light
Parameters:
  initial_brightness: 0  # Optional, default 0
Entity Bindings:
  output_channel_0: light.living_room_ceiling
```

**Use Cases:**
- Simple ceiling lights
- Basic table lamps
- Non-dimmable lights (via on/off at 100%)

---

### 2. Dimmable Light with Scenes (`dimmable_light_with_scenes`)

Advanced light with brightness control and scene support.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: 1 brightness channel (0-100%)
- **Inputs**: None
- **Scenes**: Full scene support (save, recall, undo)
- **Entity Binding**: Requires one `light` entity

**Configuration:**
```yaml
Template: dimmable_light_with_scenes
Instance Name: Dining Room Chandelier
Parameters:
  initial_brightness: 0
  transition_time: 1.0  # Fade time in seconds
Entity Bindings:
  output_channel_0: light.dining_room_chandelier
```

**Use Cases:**
- Mood lighting
- Scene-based lighting control
- Lights with automation sequences

---

### 3. RGB Color Light (`rgb_color_light`)

RGB light with color and brightness control.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: 
  - Channel 0: Brightness (0-100%)
  - Channel 1: Hue (0-360°)
  - Channel 2: Saturation (0-100%)
- **Inputs**: None
- **Scenes**: Color scene support
- **Entity Binding**: Requires one `light` entity with RGB support

**Configuration:**
```yaml
Template: rgb_color_light
Instance Name: Living Room LED Strip
Parameters:
  initial_brightness: 0
  initial_hue: 0
  initial_saturation: 0
Entity Bindings:
  output_channel_0: light.living_room_led_strip
```

**Use Cases:**
- RGB LED strips
- Color-changing bulbs
- Accent lighting

---

### 4. Wall Switch Single Button (`wall_switch_single_button`)

Single button wall switch for scene triggering.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: None
- **Inputs**: 1 button input (single press)
- **Scenes**: Trigger scenes on button press
- **Entity Binding**: Requires one `button` entity

**Configuration:**
```yaml
Template: wall_switch_single_button
Instance Name: Bedroom Wall Switch
Parameters:
  button_type: single  # single, short_long, or multi
  scene_on_press: 5  # Scene number to call on press
Entity Bindings:
  button_input_0: button.bedroom_wall_switch
```

**Use Cases:**
- Wall-mounted switches
- Scene trigger buttons
- Smart button integrations

---

### 5. Motorized Blinds (`motorized_blinds`)

Position-controlled blinds or shades.

**Specifications:**
- **Primary Group**: DSGroup.BLIND (4) - Shades
- **Outputs**: 1 position channel (0-100%, 0=closed, 100=open)
- **Inputs**: Optional binary input for manual override
- **Scenes**: Position scenes
- **Entity Binding**: Requires one `cover` entity

**Configuration:**
```yaml
Template: motorized_blinds
Instance Name: Living Room Blinds
Parameters:
  initial_position: 0  # Closed
  tilt_support: false  # Set true for tilt control
Entity Bindings:
  output_channel_0: cover.living_room_blinds
```

**Use Cases:**
- Motorized blinds
- Roller shades
- Venetian blinds with position control

---

### 6. Temperature Sensor (`temperature_sensor`)

Simple temperature sensor.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light (for integration)
- **Outputs**: None
- **Inputs**: 1 temperature sensor (-40°C to 80°C)
- **Scenes**: None
- **Entity Binding**: Requires one `sensor` entity

**Configuration:**
```yaml
Template: temperature_sensor
Instance Name: Living Room Temperature
Parameters:
  sensor_type: temperature
  unit: "°C"
  min_value: -40.0
  max_value: 80.0
Entity Bindings:
  sensor_0: sensor.living_room_temperature
```

**Use Cases:**
- Room temperature monitoring
- Climate control sensors
- HVAC integration

---

### 7. Temperature & Humidity Sensor (`temperature_humidity_sensor`)

Combined climate sensor.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: None
- **Inputs**: 
  - Sensor 0: Temperature (-40°C to 80°C)
  - Sensor 1: Humidity (0-100%)
- **Scenes**: None
- **Entity Binding**: Requires two `sensor` entities

**Configuration:**
```yaml
Template: temperature_humidity_sensor
Instance Name: Bathroom Climate
Parameters:
  temp_unit: "°C"
  humidity_unit: "%"
Entity Bindings:
  sensor_0: sensor.bathroom_temperature
  sensor_1: sensor.bathroom_humidity
```

**Use Cases:**
- Bathroom climate monitoring
- HVAC zones
- Comfort tracking

---

### 8. Motion Sensor (`motion_sensor`)

PIR motion detector.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: None
- **Inputs**: 1 binary input (motion detection)
- **Scenes**: Can trigger scenes on motion
- **Entity Binding**: Requires one `binary_sensor` entity

**Configuration:**
```yaml
Template: motion_sensor
Instance Name: Hallway Motion
Parameters:
  binary_type: motion
  inverted: false
Entity Bindings:
  binary_input_0: binary_sensor.hallway_motion
```

**Use Cases:**
- Motion-activated lighting
- Security monitoring
- Occupancy detection

---

### 9. Heating Controller (`heating_controller`)

Temperature-controlled heating device.

**Specifications:**
- **Primary Group**: DSGroup.HEATING (9) - Heating
- **Outputs**: 1 temperature setpoint channel (5-30°C)
- **Inputs**: 1 temperature sensor (current temperature)
- **Scenes**: Temperature scenes
- **Entity Binding**: Requires one `climate` entity + one `sensor` entity

**Configuration:**
```yaml
Template: heating_controller
Instance Name: Living Room Heating
Parameters:
  min_temp: 5.0
  max_temp: 30.0
  initial_temp: 20.0
Entity Bindings:
  output_channel_0: climate.living_room_heating
  sensor_0: sensor.living_room_temperature
```

**Use Cases:**
- Radiator valves
- Floor heating
- Zone heating control

---

## Vendor-Specific Templates

### Philips HUE Lily Garden Spot (`philips_hue_lily_garden_spot`)

Pre-configured for Philips HUE Lily outdoor RGB+White spotlight.

**Specifications:**
- **Primary Group**: DSGroup.YELLOW (1) - Light
- **Outputs**: 
  - Channel 0: Brightness (0-100%)
  - Channel 1: Hue (0-360°)
  - Channel 2: Saturation (0-100%)
  - Channel 3: Color Temperature (2000-6500K)
- **Inputs**: None
- **Scenes**: Full scene support
- **Entity Binding**: Requires one `light` entity with RGBW support

**Configuration:**
```yaml
Template: philips_hue_lily_garden_spot
Instance Name: Garden Spotlight 1
Parameters:
  # No additional parameters needed
Entity Bindings:
  output_channel_0: light.garden_spotlight_1
```

**Use Cases:**
- Philips HUE Lily outdoor lights
- RGB+White garden lighting
- Architectural accent lighting

---

## Creating Custom Templates

While templates provide quick deployment, you can also create devices manually for full control. See the main README for manual device creation.

### Manual Device Creation Workflow

1. Navigate to integration configuration
2. Choose "Add Device Manually"
3. Configure device parameters:
   - Name and dsUID
   - Primary and secondary groups
   - Zone assignment
4. Add outputs (channels)
5. Add inputs (sensors, binary inputs, buttons)
6. Configure entity bindings
7. Complete and announce device

### Template Parameter Override

All template parameters can be overridden during deployment:

- **initial_value**: Starting value for outputs
- **min_value/max_value**: Range constraints
- **transition_time**: Fade/transition duration
- **scene_config**: Scene behavior customization

---

## Best Practices

### Entity Binding

1. **Match Entity Domains**: Ensure bound entities match expected types
   - Brightness channels → `light` entities
   - Position channels → `cover` entities
   - Temperature sensors → `sensor` entities with temperature class
   - Motion detection → `binary_sensor` entities with motion class

2. **Entity Availability**: Verify entities exist before binding
   - Check entity IDs in Developer Tools → States
   - Ensure entities are not disabled

3. **State Compatibility**: Confirm entity states match channel expectations
   - Light brightness: 0-255 (auto-converted to 0-100%)
   - Cover position: 0-100%
   - Temperature: Numeric values in °C or °F

### Group Assignment

Choose primary groups based on device function:

- **DSGroup.YELLOW (1)**: General lighting, switches
- **DSGroup.GRAY (2)**: Shades, blinds (though use BLIND for better semantics)
- **DSGroup.BLIND (4)**: Blinds and shades (recommended)
- **DSGroup.HEATING (9)**: Climate control, heating
- **DSGroup.COOLING (10)**: Air conditioning (if supported)

### Scene Configuration

For scene-enabled devices:

1. Create device first
2. Set desired states in Home Assistant
3. Use `save_scene` service to store state as scene
4. Test scene recall with `call_scene` service
5. Configure automation to trigger scenes

---

## Troubleshooting Templates

### Template Not Found

**Symptom**: Template doesn't appear in dropdown  
**Solution**: 
- Run `refresh_templates` service
- Check template_manager.py for template definition
- Verify template YAML syntax

### Entity Binding Fails

**Symptom**: Device created but binding not working  
**Solution**:
- Verify entity exists and is available
- Check entity domain matches channel type
- Enable debug logging to see binding attempts
- Review entity state format (numeric vs. string)

### Device Not Announced

**Symptom**: Device created in HA but not visible in dSS  
**Solution**:
- Use `announce_device` service with `force: true`
- Check VDC host connection status
- Verify dsUID is valid and unique
- Review dSS logs for rejection reasons

---

## See Also

- [Main README](../README.md) - General integration documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture details
- [pyvdcapi Documentation](https://github.com/KarlKiel/pyvdcapi) - VDC-API library reference
