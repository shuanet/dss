#!/usr/bin/python3

import requests
import json
import os
import uuid
import threading
import time
import logging

from flask_socketio import SocketIO

from datetime import datetime, timedelta
from flask import Flask, request

from isa import ISA
from subscription import Subscription
from flight import Flight


class USSP():


    def __init__(self, _id, _port):
        self.id = _id
        self.read_token = None
        self.write_token = None
        self.read_headers = None
        self.write_headers = None
        self.isas = []
        self.subscriptions = []
        self.flights = []
        print("USSP %s created" % self.id)

        self.port = _port
        self.app = Flask(__name__)

        self.socketio = SocketIO(self.app)

        # to disable logging information
        log = logging.getLogger('werkzeug')
        log.disabled = True

        @self.socketio.on('TELEMETRY')
        def handle_tele(tele):
            print("telemetry received " + str(tele))

        @self.app.route("/%s" % self.id , methods=["GET"])
        def home_page():
            return ("HOMEPAGE")

        @self.app.route("/%s/flights" % self.id, methods=["GET", "POST"])
        def flights():
            if request.method == 'POST':
                #print(request.data)
                # TODO : check flight creation request completion
                # TODO : accept or refuse flight according to other flights 
                flight = self.create_flight(request.data)
                # one day automatically assign flight to ISA ? ## DO THIS WHEN START FLIGHT
                self.assign_isa_to_flight(flight)
                #isa_for_flight = input("Input ISA for flight %s : " % flight.id)
                #self.assign_isa_to_flight(flight, isa_for_flight)
                flight.status = "ACCEPTED"
                return flight.get_json()
            elif request.method == 'GET':
                return ("all flights")

        @self.app.route("/%s/flights/<string:flight_id>" % self.id, methods=['GET', 'POST'])
        def flight_information(flight_id):
            if request.method == "POST":
                return("POST flight_information")
            elif request.method == "GET":
                return ("flight_information")

        @self.app.route("/%s/flights/<string:flight_id>/start_flight", methods=['POST'])
        def start_flight(flight_id):
            ok, msg = self.start_flight(flight_id)
            return(msg)

        @self.app.route("/%s/flights/<string:flight_id>/details" % self.id, methods=["GET"])
        def get_flight_details(flight_id):
            return ("flight details")

        def run_thread_server():    
            self.app.run('localhost', _port)

        self.thread_server = threading.Thread(target=run_thread_server, daemon=True)
        self.thread_server.start()
        time.sleep(1) # give time for server to start



    def authentify_read(self):

        params = (
            ('sub', self.id),
            ('intended_audience', 'localhost'),
            ('scope', 'dss.read.identification_service_areas'),
            ('issuer', 'dummy_oauth'),
        )

        response = requests.get('http://localhost:8085/token', params=params)
        #print(response.json())

        if response.status_code == 200:
            self.read_token = response.json()["access_token"]
            self.read_headers = {
                'Authorization': 'Bearer %s' % self.read_token,
                'Content-Type': 'application/json'
            }
            print("USSP %s auth read with token %s" % (self.id, self.read_token))
        else:
            print("Error in auth read process %" % response.text)

        return response.status_code



    def authentify_write(self):

        params = (
            ('sub', self.id),
            ('intended_audience', 'localhost'),
            ('scope', 'dss.write.identification_service_areas'),
            ('issuer', 'dummy_oauth'),
        )

        response = requests.get('http://localhost:8085/token', params=params)
        #print(response.json())

        if response.status_code == 200:
            self.write_token = response.json()["access_token"]
            self.write_headers = {
                'Authorization': 'Bearer %s' % self.write_token,
                'Content-Type': 'application/json'
            }
            print("USSP %s auth write with token %s" % (self.id, self.write_token))
        else:
            print("Error in auth write process %" % response.text)

        return response.status_code


    def get_isa(self, _isa_id):

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s" % _isa_id
        response = requests.get(url, headers=self.read_headers)
        print(response.json())

        print("USSP %s attempting to get ISA %s" % (self.id, _isa_id))
        print(response.text)
        
        return response



    def create_isa(self, _name, _geometry, _time_start, _time_end):

        new_isa_id = uuid.uuid1()

        isa = ISA(new_isa_id, geometry, time_start, time_end, self.id)
        self.isas.append(isa)

        print("ISA created with id %s" % new_isa_id)
        print(isa)



    def create_isa_test(self):

        new_isa_id = uuid.uuid1()
        now = datetime.now()
        time_start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        tomorrow = datetime.now() + timedelta(days=1)
        time_end = tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ")
        name = "toulouse"

        geometry = {"footprint": {
                "vertices": [{
                        "lng": 1.206266,
                        "lat": 43.764436
                    },                               
                    {
                        "lng": 1.258522,
                        "lat": 43.500720
                    },
                    {
                        "lng": 1.631048,
                        "lat": 43.515354
                    },
                    {
                        "lng": 1.594875,
                        "lat": 43.763197
                    }                    
                ]},
                "altitude_lo": 0,
                "altitude_hi": 500
            }

        isa = ISA(name, new_isa_id, geometry, time_start, time_end, self.id)

        self.isas.append(isa)

        print("ISA created with id %s" % new_isa_id)
        print(isa)



    def submit_isa(self, _isa_id = None, _isa_name = None):

        isa_id = ''
        submitted = False
        try:
            if _isa_id is not None:
                isa = next(isa for isa in self.isas if str(isa.id) == str(_isa_id))
                isa_id = _isa_id
            elif _isa_name is not None:
                isa = next(isa for isa in self.isas if str(isa.name) == str(_isa_name))
                isa_id = isa.id
            submitted = isa.submitted
        except StopIteration:
            print("ISA not existing in USSP database")
            print("Use create_isa before submiting")

        if not submitted:
            payload = json.dumps({
                    "extents": {
                        "spatial_volume": isa.geometry,
                        "time_start": isa.time_start,
                        "time_end": isa.time_end
                    },
                    "flights_url": "http://localhost:%s/%s/%s" % (self.port, self.id, isa.id)
                })

            print("USSP %s attempting to submit ISA %s" % (self.id, isa_id))
            response = requests.request('PUT', "http://localhost:8082/v1/dss/identification_service_areas/%s" % isa_id, headers=self.write_headers, data=payload)
            #print(response.json())

            if response.status_code == 200:
                print("ISA successfully submitted")
                isa.submitted = True
            else:
                print("ISA already submitted")
            print(response.text)



    def delete_isa(self, _isa_id = None, _isa_name = None):

        isa_id = ''
        submitted = True
        try:
            print("Attempting to delete ISA from USSP database")
            if _isa_id is not None:
                isa = next(isa for isa in self.isas if str(isa.id) == str(_isa_id))
                isa_id = _isa_id
            elif _isa_name is not None:
                isa = next(isa for isa in self.isas if str(isa.name) == str(_isa_name))
                isa_id = isa.id
            submitted = isa.submitted
            del isa
            print("ISA %s deleted from local USSP database" % isa_id)
        except StopIteration:
            print("ISA not existing in USSP database")
            isa_id = _isa_id

        if submitted:
            print("Attempting to delete ISA %s from DSS database" % isa_id)
            dss_isa = self.get_isa(isa_id)

            dss_isa_version = dss_isa.json()['service_area']['version']

            url = "http://localhost:8082/v1/dss/identification_service_areas/%s/%s" % (isa_id, dss_isa_version)

            response = requests.delete(url, headers=self.write_headers)
            #print(response.json())

            if response.status_code == 200:
                print("ISA successfully deleted from DSS database")
            else:
                print("Error when attempting to delete ISA from DSS")

            print(response.text)
        else:
            print("The ISA was not submitted to DSS, cant delete from DSS")



    def get_subscription(self, _sub_id):

        print("sub_id : ", _sub_id)
        url = "http://localhost:8082/v1/dss/subscriptions/%s" % _sub_id
        response = requests.get(url, headers=self.read_headers)
        print(response.json())

        print("USSP %s attempting to get subscription %s" % (self.id, _sub_id))
        print(response.text)
        
        if response.status_code == 200:
            return response
        else:
            return  None



    def create_subscription_test(self):

        new_sub_id = uuid.uuid1()
        now = datetime.now()
        time_start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        tomorrow = datetime.now() + timedelta(days=1)
        time_end = tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ")
        name = "toulouse"

        geometry = {"footprint": {
                "vertices": [{
                        "lng": 1.206266,
                        "lat": 43.764436
                    },                               
                    {
                        "lng": 1.258522,
                        "lat": 43.500720
                    },
                    {
                        "lng": 1.631048,
                        "lat": 43.515354
                    },
                    {
                        "lng": 1.594875,
                        "lat": 43.763197
                    }                    
                ]},
                "altitude_lo": 0,
                "altitude_hi": 500
            }

        subscription = Subscription(name, new_sub_id, geometry, time_start, time_end)
        self.subscriptions.append(subscription)

        print("Subscription created with id %s" % new_sub_id)
        print(subscription)



    def create_subscription(self, _name, _geometry, _time_start, _time_end):

        new_sub_id = uuid.uuid1()

        subscription = Subscription(_name, new_sub_id, _geometry, _time_start, _time_end)
        self.subscriptions.append(subscription)

        print("Subscription created with id %s" % new_sub_id)
        print(subscription)



    def submit_subscription(self, _sub_id = None, _sub_name = None):

        sub_id = ''
        submitted = False
        try:
            if _sub_id is not None:
                subscription = next(sub for sub in self.subscriptions if str(sub.id) == str(_sub_id))
                sub_id = _sub_id
            elif _sub_name is not None:
                subscription = next(sub for sub in self.subscriptions if str(sub.name) == str(_sub_name))
                sub_id = subscription.id
            submitted = subscription.submitted
        except StopIteration:
            print("Subscription not existing in USSP database")
            print("Use create_sub before submiting")

        if not submitted:
            payload = json.dumps({
                    "extents": {
                        "spatial_volume": subscription.geometry,
                        "time_start": subscription.time_start,
                        "time_end": subscription.time_end
                    },
                    "callbacks": {
                        "identification_service_area_url": "http://localhost:%s/%s/%s" % (self.port, self.id, subscription.id)
                    }
                })

            print("USSP %s attempting to subscribe with sub_id %s" % (self.id, sub_id))
            response = requests.request('PUT', "http://localhost:8082/v1/dss/subscriptions/%s" % sub_id, headers=self.read_headers, data=payload)
            #print(response.json())

            if response.status_code == 200:
                print("Subscription successfully submitted")
                subscription.submitted = True
            else:
                print("Subscription not submitted")
            print(response.text)



    def delete_subscription(self, _sub_id = None, _sub_name = None):

        sub_id = ''
        submitted = True
        try:
            print("Attempting to delete subscription from USSP database")
            if _sub_id is not None:
                subscription = next(sub for sub in self.subscriptions if str(sub.id) == str(_sub_id))
                sub_id = _sub_id
            elif _sub_name is not None:
                subscription = next(sub for sub in self.subscriptions if str(sub.name) == str(_sub_name))
                sub_id = subscription.id
            submitted = subscription.submitted
            del subscription
            print("Subscription deleted from local USSP database")
        except StopIteration:
            print("Subscription not existing in USSP database")
            sub_id = _sub_id

        if submitted:
            print("Attempting to delete subscription from DSS database")
            dss_sub = self.get_subscription(sub_id)

            dss_sub_version = dss_sub.json()['subscription']['version']

            url = "http://localhost:8082/v1/dss/subscriptions/%s/%s" % (sub_id, dss_sub_version)

            response = requests.delete(url, headers=self.read_headers)
            #print(response.json())

            if response.status_code == 200:
                print("Subscription successfully deleted from DSS database")
            else:
                print("Error when attempting to delete sub from DSS")

            print(response.text)
        else:
            print("The subscription was not submitted to DSS, cant delete from DSS")



    def create_flight(self, _data):

        #data = json.dumps(_data.decode('utf8').replace("'", '"'))
        data = json.loads(_data.decode('utf8'))
        print(data)

        id = uuid.uuid1()
        buffer = data["buffer"]
        max_alt = data["max_alt"]
        min_alt = data["min_alt"]
        time_start = data["time_start"]
        time_end = ["time_end"]

        flight = Flight(id, buffer, max_alt, min_alt, time_start, time_end)

        self.flights.append(flight)

        return flight



    def assign_isa_to_flight(self, flight):

        # here we just check if toulouse ISA exists for the flight 
        # we consider that in our scenario all flights will take place in toulouse
        # and assign it to the flight 

        # TODO later : make something that really does the job

        for isa in self.isas:
            if isa.name == "toulouse":
                flight.assigned_isa_id = ias.id



    def start_flight(self, flight_id):

        for flight in self.flight:
            if flight.id == flight_id:
                # ASSIGN ISA AND CONFIRM FLIGHT START
                self.assign_isa_to_flight(flight)
                flight.status = "STARTED"
                return True, flight.get_json()
            else: 
                return False, "FLIGHT NOT EXISTING, REQUEST DENIED"