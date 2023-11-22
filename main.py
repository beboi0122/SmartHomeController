import json
import time

from logic.lighting import Lighting
from hardware.shiftregisters.shift_register_in import ShiftRegisterIn
from smartHome import SmartHome
import globals
from services.firebase import Firebase


def generate_state_json():
    if globals.state is None:
        state = {"state": {"rooms": {}}}
        tmp = globals.config["smart_home_config"]
        state["state"]["temperature_control"] = {"state": "OFF"}
        if "alarm_system" in tmp:
            state["state"]["alarm_system"] = {"alarm": False, "state": "OFF"}
        for room in tmp["rooms"]:
            state["state"]["rooms"][room] = {}
            if 'temperature_and_humidity' in tmp["rooms"][room]:
                state["state"]["rooms"][room]["temperature"] = -1
                state["state"]["rooms"][room]["humidity"] = -1
            if "temperature_control" in tmp["rooms"][room]:
                state["state"]["rooms"][room]["target_temperature"] = int(tmp["rooms"][room]["temperature_control"]["target_temperature"])
            if "ventilation" in tmp["rooms"][room]:
                state["state"]["rooms"][room]["target_humidity"] = int(tmp["rooms"][room]["ventilation"]["target_humidity"])
            state["state"]["rooms"][room]['functions'] = {}
            for func in tmp["rooms"][room]['functions']:
                state["state"]["rooms"][room]['functions'][func] = {"type": tmp["rooms"][room]['functions'][func]['type'],
                                                                    "state": False}
        return state
    else:
        return globals.state




globals.fireBase = Firebase()

globals.config = globals.fireBase.get_config()

globals.state = generate_state_json()

globals.smartHome = SmartHome()

if globals.is_internet_available():
    globals.fireBase.start()

globals.fireBase.send_state()



