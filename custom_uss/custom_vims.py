#!/usr/bin/python3

from crypt import methods
import json
import os
import uuid
import threading
import time
import logging
import random

from flask_socketio import SocketIO

from datetime import datetime, timedelta
from flask import Flask, request

from isa import ISA
from subscription import Subscription
from flight import Flight


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
        
        @self.app.route("/%s/vertiports" % self.id, methods=['GET', 'POST'])
        def vertiport():
            # POST A VERTIPORT
            
            # GET VERTIPORT INFO