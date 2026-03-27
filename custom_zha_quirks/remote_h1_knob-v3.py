import math
import zigpy.types as t
from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, Identify, OnOff, Ota, PowerConfiguration
from zhaquirks.xiaomi import LUMI, BasicCluster, XiaomiCustomDevice
from zhaquirks.const import (
    ARGS, BUTTON, COMMAND, COMMAND_OFF, COMMAND_TOGGLE, 
    DEVICE_TYPE, DOUBLE_PRESS, ENDPOINT_ID, ENDPOINTS, 
    INPUT_CLUSTERS, LONG_PRESS, MODELS_INFO, OUTPUT_CLUSTERS, 
    PROFILE_ID, SHORT_PRESS, LONG_RELEASE, ZHA_SEND_EVENT, 
    ALT_DOUBLE_PRESS, ALT_LONG_PRESS, ROTATED
)

# Constants for action mapping
STOP_ROTATION = "stop_rotation"
HOLD_STOP_ROTATION = "hold_stop_rotation"
ARG_DIRECTION = 'rotation_direction'

class KnobAction(t.enum8):
    off = 0x00
    start_rotation = 0x01
    rotation = 0x02
    stop_rotation = 0x03
    hold_start_rotation = 0x81
    hold_rotation = 0x82
    hold_stop_rotation = 0x83

class KnobManuSpecificCluster(BasicCluster):
    """Modified manufacturer specific cluster for 2026.3 compatibility."""
    cluster_id = 0xFCC0
    attributes = {
        0x022C: ("rotation_time_delta", t.uint16_t, True),
        0x023A: ("action", KnobAction, True),
        0x022E: ("rotation_angle", t.Single, True),
    }

    def handle_message(self, hdr, args, dst_addressing=None):
        super().handle_message(hdr, args, dst_addressing)
        # 2026.3 logic: intercepting the specific rotary action cluster
        if hdr.command_id == 0x01: # Report Attributes
            action = getattr(args, "action", None)
            if action:
                event_args = {"action": action.name}
                if action in (KnobAction.stop_rotation, KnobAction.hold_stop_rotation):
                    angle = getattr(args, "rotation_angle", 0)
                    event_args[ARG_DIRECTION] = math.copysign(1, angle)
                self.listener_event(ZHA_SEND_EVENT, action.name, event_args)

class AqaraH1KnobV3(XiaomiCustomDevice):
    """Aqara H1 Knob Quirk v3 for HA Core 2026.3.4."""
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
                INPUT_CLUSTERS: [BasicCluster, Identify.cluster_id, PowerConfiguration.cluster_id, KnobManuSpecificCluster],
                OUTPUT_CLUSTERS: [Identify.cluster_id, OnOff.cluster_id, Ota.cluster_id],
            },
            71: { # Dimmer logic
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [KnobManuSpecificCluster],
            },
        },
    }

    device_automation_triggers = {
        (SHORT_PRESS, BUTTON): {COMMAND: "single"},
        (DOUBLE_PRESS, BUTTON): {COMMAND: "double"},
        (LONG_PRESS, BUTTON): {COMMAND: "hold"},
        (ROTATED, BUTTON): {COMMAND: STOP_ROTATION},
    }
