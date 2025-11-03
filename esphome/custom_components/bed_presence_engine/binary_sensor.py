"""Binary Sensor Platform for Bed Presence Engine"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, binary_sensor, text_sensor
from esphome.const import CONF_ID, DEVICE_CLASS_OCCUPANCY

from . import bed_presence_engine_ns, BedPresenceEngine

# Configuration keys
CONF_ENERGY_SENSOR = "energy_sensor"
CONF_K_ON = "k_on"
CONF_K_OFF = "k_off"
CONF_STATE_REASON = "state_reason"

CONFIG_SCHEMA = binary_sensor.binary_sensor_schema(
    BedPresenceEngine,
    device_class=DEVICE_CLASS_OCCUPANCY
).extend(
    {
        cv.GenerateID(): cv.declare_id(BedPresenceEngine),
        cv.Required(CONF_ENERGY_SENSOR): cv.use_id(sensor.Sensor),
        cv.Optional(CONF_K_ON, default=4.0): cv.float_range(min=0.0, max=10.0),
        cv.Optional(CONF_K_OFF, default=2.0): cv.float_range(min=0.0, max=10.0),
        cv.Optional(CONF_STATE_REASON): text_sensor.text_sensor_schema(),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await binary_sensor.register_binary_sensor(var, config)

    energy_sensor = await cg.get_variable(config[CONF_ENERGY_SENSOR])
    cg.add(var.set_energy_sensor(energy_sensor))

    cg.add(var.set_k_on(config[CONF_K_ON]))
    cg.add(var.set_k_off(config[CONF_K_OFF]))

    if CONF_STATE_REASON in config:
        reason_sensor = await text_sensor.new_text_sensor(config[CONF_STATE_REASON])
        cg.add(var.set_state_reason_sensor(reason_sensor))
