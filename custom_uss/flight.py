#!/usr/bin/python3
import uas

class Flight():
    """
    Class Flight associated with UAS and USSP.
    """

    def __init__(self, _id, _uas_id, _time_start, _time_end, _dep_id, _arr_id, _ETD, _ETA, _waypoints, _diverts):
        self.id = _id
        self.uas_id = _uas_id
        self.time_start = _time_start
        self.time_end = _time_end
        self.dep_id = _dep_id
        self.arr_id = _arr_id
        self.eta = _ETD
        self.etd = _ETA
        self.waypoints = _waypoints # json of coordinates and timestamps
        self.diverts = _diverts     # json of IDs

    def __str__(self):
        return "FLIGHT ID:%s \nUAS ID:%s \nTIME START:%s \nTIME END:%s \nDEPARTURE ID:%s \nARRIVAL ID:%s \n\
            ETD:%s \nETA:%s \nWAYPOINTS:%s \nDIVERTS:%s" % (self.id, self.uas_id, self.time_start, self.time_end,
            self.dep_id, self.arr_id, self.eta, self.etd, self.waypoints, self.diverts)

