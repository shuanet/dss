#!/usr/bin/python3

import json
import uuid
from flask_socketio import SocketIO

from datetime import datetime, timedelta
from flask import Flask, request

from vertiport import Vertiport
# from custom_uss.custom_uss import USSP


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
		self.flight_sequence = []
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
	def create_vertiport_test(self, file_name):
		"""
		Create a predetermined Vertiport for testing.
		"""
		f = open(file_name, "r")
		data = json.load(f)
		print(data)

		_vertiport_id = uuid.uuid1()
		_time_start = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
		_time_end = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

		vertiport = Vertiport(_vertiport_id, data[1], data[3], data[4], data[5], data[6], _time_start, _time_end, data[9], data[10], data[11], data[12], data[13])
		self.vertiports.append(vertiport)

		print("Vertiport created with id: %s" % _vertiport_id)
		print(vertiport)


	def delete_vertiport(self, _vertiport_name = None):
		"""
		Delete a vertiport.
		"""
		try:
			print("Attempting to delete Vertiport from VIMS database")

			if _vertiport_name is not None:
				vertiport = next(vertiport for vertiport in self.vertiports if str(vertiport.name) == str(_vertiport_name))
				vertiport_id = vertiport.id
			del vertiport
			print("Vertiport %s deleted from local VIMS database" % vertiport_id)
		except StopIteration:
			print("Vertiport not existing in VIMS database")
	

	# def check_permission(self)


	# def subscribe_vertiport


	# def unsubscribe_vertiport


	def get_vertiport(self, _vertiport_id):
		"""
		Get Vertiport details by its ID.
		"""
		try:

			url = "http://localhost:8082/v1/vertiports/%s" % _vertiport_id
			response = request.get(url, headers=self.read_headers)
			print(response.json())

			print("VIMS %s attempting to get Vertiport %s" % (self.id, _vertiport_id))
			print(response.text)
			
			return response
		except:
			print("No veretiport with id %s in this VIMS" % _vertiport_id)


	# def update_vertiport_slots(self, _vertiport_id, flight_id)


	def check_slots_availability(self, _vertiport_id, _time):
		# search the vertiport
		try:
			_slots = self.get_vertiport(_vertiport_id).json()
			
		except:
			print("Vertiport with id: " + str(_vertiport_id) + " does not exist in VIMS: " + str(self.id))

		# check the slots availability
		try:
			for  i in range(len(_slots)):
				if (_slots[i].time_start <= _time) and (_time <= _slots[i].time_end) and (_slots[i].available == True):
					print("Available slot: " + str(_slots[i]) + "from " + str(_slots[i].time_start) + "to " + str(_slots[i].time_end))

		except:
			print("Unavailable slot at " + _time)
		
	

	# def activate_slot(self)


	# def get_flight_ussp(self, flight_id)


	# def compute_flight_sequence(self)	