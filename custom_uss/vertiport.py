#!usr/bin/python3

import json
import datetime

# only single vertiport

# PARAMETERS
# static_info = [name, lat, lon, type, t_start, t_end]
# slots_schedule = [[t_start, t_end, available, flight_# id, type], [t_start, t_end, ...]]


class Vertiport():

	def __init__(self, _id, _static_info, _FATO_status, _parking_stands, _ground_handling, _evtol_elp, _slot_schedule):
		self.id = _id
		self.static_info = _static_info				#json
		self.FATO_status = _FATO_status
		self.parking_stands = _parking_stands
		self.ground_handling = _ground_handling
		self.evtol_elp = _evtol_elp
		self.slot_schedule = _slot_schedule			#json


	def get_static_info_json(self):
		
		static_info_json = json.dumps({
			"id": str(self.id),
			"name": str(self.static_info[0]),
			"location": {
				"lat": self.static_info[1],
				"lon": self.static_info[2]
			},
			"type": str(self.static_info[3]),
			"time_start": datetime(self.static_info[4]),
			"time_end": datetime(self.static_info[5])
		})

		return static_info_json

	def get_slots_json(self):
		
		slots_json = json.dumps({
			
		})

		return slots_json