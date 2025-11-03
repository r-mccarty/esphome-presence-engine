"""
Bed Presence Engine Custom Component for ESPHome - Phase 1

This component implements z-score based presence detection:
- Statistical normalization (z-score calculation)
- Simple threshold comparison with hysteresis
- No debouncing or temporal filtering (Phase 1)
"""
import esphome.codegen as cg
from esphome.components import binary_sensor

DEPENDENCIES = []
AUTO_LOAD = ["binary_sensor"]

# Define the namespace and class
bed_presence_engine_ns = cg.esphome_ns.namespace("bed_presence_engine")
BedPresenceEngine = bed_presence_engine_ns.class_(
    "BedPresenceEngine",
    cg.Component,
    binary_sensor.BinarySensor
)
