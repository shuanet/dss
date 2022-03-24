<<<<<<< HEAD
#!/usr/bin/python3
import uas

class Flight():
    """
    Class Flight associated with UAS and USSP.
    """

    def __init__(self, _id, _uas_id, _operator, _time_start, _time_end, _dep_id, _arr_id, _ETD, _ETA, _waypoints, _diverts):
        self.id = _id
        self.uas_id = _uas_id
        self.operator = _operator
        self.time_start = _time_start
        self.time_end = _time_end
        self.dep_id = _dep_id
        self.arr_id = _arr_id
        self.eta = _ETD
        self.etd = _ETA
        self.waypoints = _waypoints # json of coordinates and timestamps
        self.diverts = _diverts     # json of IDs

    def __str__(self):
        return "FLIGHT ID:%s \nUAS ID:%s \nOPERATOR:%s \nTIME START:%s \nTIME END:%s \nDEPARTURE ID:%s \nARRIVAL ID:%s \n\
            ETD:%s \nETA:%s \nWAYPOINTS:%s \nDIVERTS:%s" % (self.id, self.uas_id, self.operator, self.time_start,
            self.time_end, self.dep_id, self.arr_id, self.eta, self.etd, self.waypoints, self.diverts)

=======
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
>>>>>>> 8390865225a9ee0052e5d946beb76e3b4c53f8dd
