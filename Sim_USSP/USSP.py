#!/usr/bin/python3

import uuid
import json
import requests


class USSP():
    """
    USSPs cretaing class for interacting with the API as the Postman collection plans and suggests.
    """
    def __init__(self, _id, _db_port):
        self.id = _id
        self.db_port = _db_port
        self.write_token = None
        self.read_token = None
        self.test_isa_id = "3e66732f-985e-4043-950a-dea2c3881ec5"
        self.read_headers = None
        self.write_headers = None
        self.isa_ids = []
        self.sub_ids = []
        print("USSP %s created", self.id)

    def authentify_read(self):
        """
        Get the token for reading API info.
        """
        print("Authentifying USSP %s",  self.id)
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
            print("USSP %s auth read with token %s", (self.id, self.read_token))
        else:
            print("Error in auth read process %", response.text)



    def authentify_write(self):
        """
        Get the token for writting to the API.
        """
        print("Authentifying USSP %s", self.id)
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
            print("USSP %s auth write with token %s", (self.id, self.write_token))
        else:
            print("Error in auth write process %", response.text)


    def get_isa(self, _isa_id = None):
        """
        Get the USSPs attempting to reach ISAs. 
        """
        if _isa_id is None:
            isa_id = self.test_isa_id
        else:
            isa_id = _isa_id

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s" % isa_id
        response = requests.get(url, headers=self.read_headers)

        print("USSP %s attempting to get ISA %s", (self.id, isa_id))
        print(response.text)
        #version = response.json()['service_area']['version']


    def create_isa(self):
        """
        Initiate ISA flights database with CrockroachDB and create new ISAs.
        """
        # initiate ISA flights database
        # create cockroach database to store flights
        # os.system("cockroach start-single-node \
        #     --insecure \
        #     --store=node%s \
        #     --http-addr=localhost:%s \
        #     --listen-addr=localhost:2%s \
        #     --background" \
        #      % (self.db_port, self.db_port, self.db_port))

        # create new ISA
        new_isa_id = uuid.uuid1()
        self.isa_ids.append(new_isa_id)

        url = "http://localhost:8082/v1/dss/identification_service_areas/%s" % new_isa_id
        
        payload = json.dumps({
            "extents": {
                "spatial_volume": {
                    "footprint": {
                        "vertices": [
                            {"lng": 1.4813,"lat": 43.5624},
                            {"lng": 1.4789,"lat": 43.56478},
                            {"lng": 1.4821,"lat": 43.5666}]
                        },
                        "altitude_lo": 0,"altitude_hi": 122
                    },
                    "time_start": "2023-03-02T09:48:12.154Z","time_end": "2023-03-02T09:53:14.155Z"
                },
                #"flights_url": "http://localhost:%s" % self.db_port
                "flights_url": "https://example.com/isa"
            })

        print("USSP %s attempting to create ISA %s", (self.id, self.test_isa_id))
        response = requests.put(url, headers=self.write_headers, data=payload)
        print(response.text)

        flights_url = response.json()['service_area']['flights_url']
        isa_id = response.json()['service_area']['id']

        return isa_id


    def subscribe(self):
        """
        Get info from ISAs and PUT a subscription.
        """
        sub_id = uuid.uuid1()
        self.sub_ids.append(sub_id)
        # get info from isa_id
        payload = json.dumps({
            "extents": {
                "spatial_volume": {
                    "footprint": {
                        "vertices": [
                            {"lng": 1.4813,"lat": 43.5624},
                            {"lng": 1.4789,"lat": 43.56478},
                            {"lng": 1.4821,"lat": 43.5666}]
                        },
                        "altitude_lo": 0,"altitude_hi": 122
                    },
                    "time_start": "2023-03-02T09:48:12.154Z","time_end": "2023-03-02T09:53:14.155Z"
                },
                "callbacks": {
                    #"identification_service_area_url": "http://localhost:8082"
                    "identification_service_area_url": "https://example.com/isas"
                }
            })

        print("USSP %s attempting to subscribe with sub_id %s", (self.id, sub_id))
        response = requests.request('PUT', "http://localhost:8082/v1/dss/subscriptions/%s" % sub_id, headers=self.read_headers, data=payload)

        print(response.text)