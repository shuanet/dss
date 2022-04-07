#!/usr/bin/python3

import json
import uuid

from flask_socketio import SocketIO

from datetime import datetime, timedelta
from flask import Flask, request

from vertiport import Vertiport


class VIMS():
    """
    VIMS Management
    """
    def __init__(self, _id, _port):
        self.id = _id
        self.read_token = None
        self.write_token = None
        self.read_headers = None
        self.write_headers = None
        self.vertiports = []
        print("VIMS %s created" % self.id)

        self.port = _port
        self.app = Flask(__name__)

        self.socketio = SocketIO(self.app)

        @self.app.route("/%s" % self.id, methods=['GET'])
        def homepage():
            return ("VIMS HOMEPAGE")
    
    
    def authentify_read(self):
        """
        Get the token for reading requests.
        """
        params = (
            ('sub', self.id),
            ('intended_audience', 'localhost'),
            ('scope', 'vims.read.vertiports'),
            ('issuer', 'dummy_oauth'),
        )

        response = request.get('http://localhost:8085/token', params=params)
        print(response.json())

        if response.status_code == 200:
            self.read_token = response.json()["access_token"]
            self.read_headers = {
                'Authorization': 'Bearer %s' % self.read_token,
                'Content-Type': 'application/json'
            }
            print("VIMS %s auth read with token %s" % (self.id, self.read_token))
        else:
            print("Error in auth read process %ss" % response.text)

        return response.status_code

    def authentify_write(self):
        """
        Get the token for writing requests.
        """
        params = (
            ('sub', self.id),
            ('intended_audience', 'localhost'),
            ('scope', 'vims.write.vertiports'),
            ('issuer', 'dummy_oauth'),
        )

        response = request.get('http://localhost:8085/token', params=params)
        print(response.json())

        if response.status_code == 200:
            self.write_token = response.json()["access_token"]
            self.write_headers = {
                'Authorization': 'Bearer %s' % self.write_token,
                'Content-Type': 'application/json'
            }
            print("VIMS %s auth write with token %s" % (self.id, self.write_token))
        else:
            print("Error in auth write process %" % response.text)

        return response.status_code

    """
    VERTIPORT METHODS.
    """
    
    # def check_permission(self)

    # on ussp
    def get_vertiport(self, _vertiport_id):
        """
        Get Vertiport details by its ID.
        """
        url = "http://localhost:8082/v1/vertiports/%s" % _vertiport_id
        response = request.get(url, headers=self.read_headers)
        print(response.json())

        print("VIMS %s attempting to get Vertiport %s" % (self.id, _vertiport_id))
        print(response.text)
        
        return response
