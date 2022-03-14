#!/usr/bin/python3

import json
import os
import uuid
import threading
import time

from datetime import datetime, timedelta
from isa import ISA
from subscription import Subscription

from flask import Flask
import requests


class USSP():
    """
    USSP actions with API
    """
    def __init__(self, _id, _port):
        self.id = _id
        self.read_token = None
        self.write_token = None
        self.read_headers = None
        self.write_headers = None
        self.isas = []
        self.subscriptions = []
        self.uas = []
        print("USSP %s created" % self.id)

        self.port = _port
        self.app = Flask(__name__)

        @self.app.route("/%s" % self.id , methods=['GET'])
        def home_page():
            return ("HOMEPAGE")

        @self.app.route("/%s/flights" % self.id, methods=["GET"])
        def get_all_flights():
            return ("all flights")

        @self.app.route("/%s/flights/<string:flight_id>/details" % self.id, methods=["GET"])
        def get_flight_details(flight_id, methods=["GET"]):
            return ("flight details")

        def run_thread_server():    
            self.app.run('localhost', _port)

        self.thread_server = threading.Thread(target=run_thread_server, daemon=True)
        self.thread_server.start()
        time.sleep(1) # give time for server to start



    def authentify_read(self):
        """
        Get the token for reading requests.
        """
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
            print("Error in auth read process %ss" % response.text)



    def authentify_write(self):
        """
        Get the token for writing requests.
        """
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
            print("Error in auth write process %s" % response.text)

    """
    ISA METHODS.
    """

    def get_isa(self, _isa_id):
        """
        Get ISA details by its ID.
        """
        url = "http://localhost:8082/v1/dss/identification_service_areas/%s" % _isa_id
        response = requests.get(url, headers=self.read_headers)
        print(response.json())

        print("USSP %s attempting to get ISA %s" % (self.id, _isa_id))
        print(response.text)
        
        return response



    def create_isa(self, _name, _geometry, _time_start, _time_end):
        """
        Create an ISA.
        """
        new_isa_id = uuid.uuid1()

        isa = ISA(new_isa_id, _geometry, _time_start, _time_end, self.port)
        self.isas.append(isa)

        print("ISA created with id %s" % new_isa_id)
        print(isa)



    def create_isa_test(self):
        """
        Create a predetermined ISA "toulouse" for testing.
        """
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

        isa = ISA(name, new_isa_id, geometry, time_start, time_end)

        self.isas.append(isa)

        print("ISA created with id %s" % new_isa_id)
        print(isa)



    def submit_isa(self, _isa_id = None, _isa_name = None):
        """
        Sybmit ISA to API by its ID or Name.
        """
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
        """
        Deleting an ISA by its ID or its Name.
        """
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


    """
    SUBSCRIPTION METHODS.
    """
    def get_subscription(self, _sub_id):
        """
        Get a Sub by its ID.
        """
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
        """
        Create a predetermined Sub with Name 'toulouse' for testing.
        """
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
        """
        Create a Sub.
        """
        new_sub_id = uuid.uuid1()

        subscription = Subscription(_name, new_sub_id, _geometry, _time_start, _time_end)
        self.subscriptions.append(subscription)

        print("Subscription created with id %s" % new_sub_id)
        print(subscription)



    def submit_subscription(self, _sub_id = None, _sub_name = None):
        """
        Submit a Sub to API by its ID or Name.
        """
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
        """
        Delete a Sub by its ID or Name.
        """
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

    """
    FLIGHTS METHODS.
    """

    def get_flight(self, _flight_id):
        url = "http://localhost:8082/v1/dss/flights/%s" % _flight_id
        response = requests.get(url, headers=self.read_headers)

        print(response.json)

        print("USSP %s attempting to get flight %s" % (self.id, _flight_id))
        print(response.text)
        
        return response
    

    
    def get_telemetry(self, _flight_id):
        