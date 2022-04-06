#!usr/bin/python3

import json
import datetime

# only single vertiport

# PARAMETERS
# pàrking_stands = [type, available, flight_id, charging_progress]
# slots_schedule = [t_start, t_end, available, flight_id, type]


class Vertiport():

	def __init__(self, _id, _name, _type, _lat, _lon, _altitude, _time_start, _time_end, _FATO_status, _parking_stands, _ground_handling, _evtol_elp, _slot_schedule):
		self.id = _id
		self.name = _name
		self.type = _type
		self.lat = _lat
		self.lon = _lon
		self.altitude = _altitude
		self.time_start = _time_start
		self.time_end = _time_end
		self.FATO_status = _FATO_status
		self.parking_stands = _parking_stands		#json
		self.ground_handling = _ground_handling
		self.evtol_elp = _evtol_elp
		self.slot_schedule = _slot_schedule			#json


	def get_parking_stands_json(self):
		
		parking_json = json.dumps({
			"parking_id":{
				"type": datetime(self.parking_stands[0]),
				"available": self.parking_stands[1],
				"flight_id": str(self.parking_stands[2]),
				"charging_progress": self.parking_stands[3]
			}
		})

		return parking_json

	def get_slots_json(self):
		
		slots_json = json.dumps({
			"slot_id":{
				"time_start": datetime(self.slot_schedule[0]),
				"time_end": datetime(self.slots_json[1]),
				"available": self.slot_schedule[2],
				"flight_id": str(self.slot_schedule[3]),
				"type": str(self.slot_schedule[4])
			}
		})

		return slots_json