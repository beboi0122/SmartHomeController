import threading
import time

import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import os
import json
import globals

class Firebase:
    def __init__(self):
        if globals.is_internet_available():
            self.open_firebase()
        else:
            self.user_json = None
            self.callback_done = None
            self.cred = None
            self.app = None
            self.db = None
            self.interrupt_doc_ref = None
            self.state_doc_ref = None
            self.config_doc_ref = None
            self.first_interrupt = None
            self.doc_watch = None
            self.config = None

    def open_firebase(self):
        with open(os.path.join(os.getcwd(), "services/user.json"), "r") as json_file:
            self.user_json = json.load(json_file)
        self.callback_done = threading.Event()

        self.cred = credentials.Certificate(os.path.join(os.getcwd(), "services/serviceAccountKey.json"))
        self.app = firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

        self.interrupt_doc_ref = self.db.collection(u'user_interrupt').document(self.user_json["uid"])
        self.state_doc_ref = self.db.collection(u'states').document(self.user_json["uid"])
        self.config_doc_ref = self.db.collection(u'configs').document(self.user_json["uid"])

        self.first_interrupt = True

        self.doc_watch = None
    def send_state(self):
        if globals.is_internet_available():
            self.state_doc_ref.update({"state": json.dumps(globals.state)})

    def on_snapshot(self, doc_snapshot, changes, read_time):
        if not self.first_interrupt:
            user_interrupt = json.loads(doc_snapshot[0].get("interrupt"))
            if "global_temperature_controll" in user_interrupt:
                if user_interrupt["global_temperature_controll"] == "HEATING":
                    globals.global_heating = True
                    globals.global_cooling = False
                    globals.state["state"]["temperature_control"]["state"] = "HEATING"
                    for room_name in globals.smartHome.rooms:
                        room = globals.smartHome.rooms[room_name]
                        if room.temp_control is not None:
                            room.temp_control.status_changed("HEATING")
                elif user_interrupt["global_temperature_controll"] == "COOLING":
                    globals.global_heating = False
                    globals.global_cooling = True
                    globals.state["state"]["temperature_control"]["state"] = "COOLING"
                    for room_name in globals.smartHome.rooms:
                        room = globals.smartHome.rooms[room_name]
                        if room.temp_control is not None:
                            room.temp_control.status_changed("COOLING")
                elif user_interrupt["global_temperature_controll"] == "OFF":
                    globals.global_heating = False
                    globals.global_cooling = False
                    globals.state["state"]["temperature_control"]["state"] = "OFF"
                    for room_name in globals.smartHome.rooms:
                        room = globals.smartHome.rooms[room_name]
                        if room.temp_control is not None:
                            room.temp_control.status_changed("OFF")
                self.send_state()
            elif "target_temperature" in user_interrupt:
                globals.state["state"]["rooms"][user_interrupt["room"]]["target_temperature"] = int(user_interrupt["target_temperature"])
                globals.smartHome.rooms[user_interrupt["room"]].temp_control.target_temperature = int(user_interrupt["target_temperature"])
                globals.smartHome.rooms[user_interrupt["room"]].temp_control.status_changed("target_temperature")
                self.send_state()
            elif "target_humidity" in user_interrupt:
                globals.state["state"]["rooms"][user_interrupt["room"]]["target_humidity"] = int(user_interrupt["target_humidity"])
                globals.smartHome.rooms[user_interrupt["room"]].ventilation.target_humidity = int(user_interrupt["target_humidity"])
                globals.smartHome.rooms[user_interrupt["room"]].ventilation.status_changed("target_humidity")
                self.send_state()
            elif "alarm_system" in user_interrupt:
                globals.state["state"]["alarm_system"]["state"] = user_interrupt["alarm_system"]
                globals.smartHome.alarm_system.status_changed(user_interrupt["alarm_system"])
                self.send_state()
            elif "state" in user_interrupt and user_interrupt["state"] == "RESET":
                self.notofy_function(user_interrupt)
            else:
                globals.state["state"]["rooms"][user_interrupt["room"]]["functions"][user_interrupt["function"]]["state"] = \
                user_interrupt["state"]
                self.send_state()
                self.notofy_function(user_interrupt)
        else:
            self.first_interrupt = False

    def start(self):
        self.doc_watch = self.interrupt_doc_ref.on_snapshot(self.on_snapshot)

    def notofy_function(self, user_interrupt):
        # print(user_interrupt)
        globals.smartHome.rooms[user_interrupt["room"]].functions[user_interrupt["function"]].status_changed(user_interrupt["state"])


    def get_config(self):
        if globals.is_internet_available():
            return json.loads(self.config_doc_ref.get().to_dict()["config"])
        else:
            # load SmartHome.json from file
            with open(os.path.join(os.getcwd(), "SmartHome.json"), "r") as json_file:
                return json.load(json_file)