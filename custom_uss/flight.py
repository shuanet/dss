#!usr/bin/python3

import json

# only single flights
# 

class Flight():

	def __init__(self, id, buffer, max_alt, min_alt, time_start, time_end):
		self.id = id
		self.buffer = buffer
		self.max_alt = max_alt
		self.min_alt = min_alt
		self.time_start = time_start
		self.time_end = time_end
		self.assigned_isa_id = None
		self.status = None
		self.telemetry_started = False
		self.last_telemetry_report_timestamp = None

	def get_json(self):

		flight_json = json.dumps({
				"id": str(self.id),
				"geometry": {
					"buffer": str(self.buffer),
					"max_alt": str(self.max_alt),
					"min_alt": str(self.min_alt),
					"time_start": str(self.time_start),
					"time_end": str(self.time_end),
				},
				"isa": str(self.assigned_isa_id),
				"status": str(self.status),
			})

		return flight_json
