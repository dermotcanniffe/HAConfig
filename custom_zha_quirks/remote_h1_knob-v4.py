import math
import zigpy.types as t
from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, Identify, OnOff, Ota, PowerConfiguration
from zhaquirks.xiaomi import LUMI, BasicCluster, XiaomiCustomDevice, XiaomiPowerConfiguration
from zhaquirks.const import (
    ARGS, BUTTON, COMMAND, DEVICE_TYPE, ENDPOINTS, 
    INPUT_CLUSTERS, MODELS_INFO, OUTPUT_CLUSTERS, 
    PROFILE_ID, SHORT_PRESS, DOUBLE_PRESS, LONG_PRESS, 
    ZHA_SEND_EVENT, ROTATED
)

# New 2026.3 naming conventions
STOP_ROTATION = "stop_rotation"
ARG_DIRECTION = "rotation_direction"

class KnobManuSpecificCluster(BasicCluster):
    cluster_id = 0xFCC0
    
    # Modern attribute definitions per PR 4735
    attributes = BasicCluster.attributes.copy()
    attributes.update({
        0x0009: ("operation_mode", t.uint8_t, True),
        0x022E: ("rotation_angle", t.Single, True),
        0x023A: ("action", t.uint8_t, True),
    })

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        # Rotary logic: 0x023A is the action trigger in post-refactor Aqara firmware
        if attrid == 0x023A:
            event_args = {"value": value}
            if value in [3, 131]: # stop_rotation codes
                angle = self._attr_cache.get(0x022E, 0)
                event_args[ARG_DIRECTION] = math.copysign(1, angle)
            self.listener_event(ZHA_SEND_EVENT, f"action_{value}", event_args)

class AqaraH1KnobV4(XiaomiCustomDevice):
    """Post-PR 4735 Compatibility Quirk."""
    signature = {
        MODELS_INFO: [(LUMI, "lumi.remote.rkba01")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT_SWITCH,
                INPUT_CLUSTERS: [Basic.cluster_id, PowerConfiguration.cluster_id, Identify.cluster_id],
                OUTPUT_CLUSTERS: [Identify.cluster_id, OnOff.cluster_id, Ota.cluster_id],
            },
        },
    }
    replacement = {
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    BasicCluster, 
                    Identify.cluster_id, 
                    XiaomiPowerConfiguration, # Use unified class from PR 4735
                    KnobManuSpecificCluster
                ],
                OUTPUT_CLUSTERS: [Identify.cluster_id, OnOff.cluster_id, Ota.cluster_id],
            },
            71: { # Consolidate secondary EP
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [KnobManuSpecificCluster],
            }
        },
    }

    device_automation_triggers = {
        (SHORT_PRESS, BUTTON): {COMMAND: "action_1"},
        (DOUBLE_PRESS, BUTTON): {COMMAND: "action_2"},
        (LONG_PRESS, BUTTON): {COMMAND: "action_129"},
        (ROTATED, BUTTON): {COMMAND: "action_3"},
    }
