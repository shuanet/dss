#!/usr/bin/python3

import requests
import json
import os
import uuid
import threading
import time

from isa import ISA
from subscription import Subscription

from datetime import datetime, timedelta

from flask import Flask

class USSP():


    def __init__(self, _id, _port):
        self.id = _id
        self.read_token = None
        self.write_token = None
        self.read_headers = None
        self.write_headers = None
        self.isas = []
        self.subscriptions = []
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



    def get_isa(self, _isa_id):

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s" % _isa_id
        response = requests.get(url, headers=self.read_headers)

        print("USSP %s attempting to get ISA %s" % (self.id, _isa_id))
        print(response.text)
        
        return response



    def create_isa(self, _name, _geometry, _time_start, _time_end):

        new_isa_id = uuid.uuid1()

        isa = ISA(new_isa_id, geometry, time_start, time_end, self.port)
        self.isas.append(isa)

        print("ISA created with id %s" % new_isa_id)
        print(isa)



    def create_isa_test(self):

        new_isa_id = uuid.uuid1()
        now = datetime.now()
        time_start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        tomorrow = datetime.now() + timedelta(days=1)
        time_end = tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ")
        name = "TOULOUSE"

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


    def submit_isa(self, _isa_id):

        isa = next(isa for isa in self.isas if str(isa.id) == str(_isa_id))

        payload = json.dumps({
              "extents": {
                "spatial_volume": isa.geometry,
                "time_start": isa.time_start,
                "time_end": isa.time_end
              },
              "flights_url": "http://localhost:%s/%s/%s" % (self.port, self.id, isa.id)
            })

        print(payload)

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s" % isa.id

        print("USSP %s attempting to submit ISA %s" % (self.id, isa.id))
        response = requests.put(url, headers=self.write_headers, data=payload)
        print(response.text)



    def delete_isa(self, _isa_id):

        try:
            isa = next(isa for isa in self.isas if str(isa.id) == str(_isa_id))
        except StopIteration:
            print("ISA not existing in USSP database")
            print("Attempting to delete ISA from DSS database")

        dss_isa = self.get_isa(_isa_id)
        dss_isa_version = dss_isa.json()['service_area']['version']

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s/%s" % (_isa_id, dss_isa_version)

        response = requests.delete(url, headers=self.write_headers)

        if response.status_code == 200:
            del isa
        else:
            print("Error when attempting to delete ISA")
            print("Maybe ISA was not submited to DSS")

        print(response.text)


    # intended to delete remaining ISAs in the DSS not deleted because of an error in the code 
    def delete_dss_isa(self, _isa_id):

        dss_isa = self.get_isa(_isa_id)
        dss_isa_version = dss_isa.json()['service_area']['version']

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s/%s" % (_isa_id, dss_isa_version)

        response = requests.delete(url, headers=self.write_headers)

        if response.status_code == 200:
            print("ISA deleted")
        else:
            print("Error when attempting to delete ISA")

        print(response.text)



    def get_subscription(self, _sub_id):

        url = "http://localhost:8082/v1/dss/subscriptions/%s" % _sub_id
        response = requests.get(url, headers=self.read_headers)

        print("USSP %s attempting to get subscription %s" % (self.id, _sub_id))
        print(response.text)
        
        return response



    def create_subscription_test(self):

        new_sub_id = uuid.uuid1()
        now = datetime.now()
        time_start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        tomorrow = datetime.now() + timedelta(days=1)
        time_end = tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ")
        name = "TOULOUSE"

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



    def submit_subscription(self, _sub_id):

        subscription = next(sub for sub in self.subscriptions if str(sub.id) == str(_sub_id))

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


        print("USSP %s attempting to subscribe with sub_id %s" % (self.id, _sub_id))
        response = requests.request('PUT', "http://localhost:8082/v1/dss/subscriptions/%s" % _sub_id, headers=self.read_headers, data=payload)

        print(response.text)



    def delete_subscription(self, _sub_id):

        try:
            subscription = next(sub for sub in self.subscriptions if str(sub.id) == str(_sub_id))
        except StopIteration:
            print("Subscription not existing in USSP database")
            print("Attempting to delete subscription from DSS database")

        dss_sub = self.get_subscription(_sub_id)
        dss_sub_version = dss_sub.json()['subscription']['version']

        url = "http://localhost:8082/v1/dss/subscriptions/%s/%s" % (_sub_id, dss_sub_version)

        response = requests.delete(url, headers=self.read_headers)

        if response.status_code == 200:
            del subscription
            print("Subscription successfully deleted")
        else:
            print("Error when attempting to delete sub")

        print(response.text)



    # intended to delete remaining subscriptions in the DSS not deleted because of an error in the code 
    def delete_dss_subscription(self, _sub_id):

        dss_sub = self.get_subscription(_sub_id)
        dss_sub_version = dss_sub.json()['subscription']['version']

        url = "http://localhost:8082/v1/dss/subscriptions/%s/%s" % (_sub_id, dss_sub_version)

        response = requests.delete(url, headers=self.read_headers)

        if response.status_code == 200:
            print("Subscription successfully deleted")
        else:
            print("Error when attempting to delete sub")

        print(response.text)