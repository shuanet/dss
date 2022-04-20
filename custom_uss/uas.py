#!/usr/bin/python3

class UAS():

    """
    Define a UAS class for getting telemetry and vehicle info.

    _op_status --> ground or airborne
    _lat and _lon in degrees
    _h_speed and _v_speed in m/s

    May add attributes related to Sub and ISA in the future.
    """

    def __init__(self, _id, _uas_type, _time_start, _time_end, _op_status, _operator, _lat, _long, _alt, _track_dir, _h_speed, _v_speed):
        
        self.id = _id 
        self.uas_type = _uas_type
        self.time_start = _time_start
        self.time_end = _time_end
        self.op_status = _op_status
        self.operator = _operator
        self.lat = _lat
        self.long = _long
        self.alt = _alt
        self.track_dir = _track_dir
        self.h_speed = _h_speed
        self.v_speed = _v_speed

    def __str__(self):
        return "UAS ID:%s \nTYPE:%s \nTIME START:%s \nTIME END:%s \nOPERATION STATUS:%s \nOPERATOR:%s \n\
            LATITUDE:%s \nLONGITUDE:%s \nALTITUDE:%s \nTRACK DIRECTION:%s \nHORIZONTAL SPEED:%s \nVERTICAL SPEED:%s" \
            % (self.id, self.uas_type, self.time_start, self.time_end, self.op_status, self.operator, 
            self.lat, self.long, self.alt, self.track_dir, self.h_speed, self.v_speed)

