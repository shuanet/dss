#!/usr/bin/python3

import sys, os

import simpy
import csv
import random
import requests
import json
import subprocess
import signal
import socketio

PPRZ_HOME = os.getenv("PAPARAZZI_HOME", os.path.normpath(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PPRZ_HOME + "/var/lib/python")
sys.path.append(PPRZ_HOME + "/sw/lib/python")

import utils

from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage

from telemetry_agent import Telemetry_Agent

## SIMULATION PARAMS ##

TIMSESTEP = 0.01 # x10 is max for pprz
TELEMETRY_TIMESTEP = 5 # period for telemetry report to be sent to ussp
FP_SEND_WINDOW_START = 20 # time when agent can start sending fp
FP_SEND_WINDOW_END = 10 # time when agent can't send fp anymore
SIMU_START_TIME = utils.to_sec("5:37:49 AM") - FP_SEND_WINDOW_START * 60 ## 1 min before first flight can send fp
V1_V2_TIME = 20 * 60
V1_V3_TIME = 25 * 60
USSP1 = {"id": "ussp1", "port": 9091}
USSP2 = {"id": "ussp2", "port": 9092}
USSP_LIST = [USSP1]

run_with_pprz = False

# PPRZ AC pools (10 per Vi -> Vj) => necessary because we have limited AC ressources in paparazzi
# the same AC can't be in flight twice at the same time(obviousy)
# therefore we need to check if AC is available before making it take off
# and free the ressource before we kill the process
# {pprz_id:True/False}, True if AC is available, False otherwise
# I expect 10 will be enough but if we have much delays it may not be enough
# in this case we'll add some more, hoping that it won't be too much for the computer power
L_AC_V1V2 = {4:True, 5:True, 8:True, 9:True, 10:True, 11:True, 12:True, 14:True, 15:True, 16:True}
L_AC_V1V3 = {17:True, 18:True, 20:True, 22:True, 23:True, 25:True, 26:True, 27:True, 28:True, 29:True}
L_AC_V2V1 = {30:True, 32:True, 33:True, 34:True, 35:True, 36:True, 38:True, 39:True, 40:True, 43:True}
L_AC_V3V1 = {44:True, 45:True, 46:True, 47:True, 48:True, 49:True, 50:True, 51:True, 52:True, 53:True}

PPRZ_ID_NAME = {4:"AC_V1V2_1", 5:"AC_V1V2_2", 8:"AC_V1V2_3", 9:"AC_V1V2_4", 
	10:"AC_V1V2_5", 11:"AC_V1V2_6", 12:"AC_V1V2_7", 14:"AC_V1V2_8", 15:"AC_V1V2_9", 
	16:"AC_V1V2_10",17:"AC_V1V3_1", 18:"AC_V1V3_2", 20:"AC_V1V3_3", 22:"AC_V1V3_4", 
	23:"AC_V1V3_5", 25:"AC_V1V3_6", 26:"AC_V1V3_7", 27:"AC_V1V3_8", 28:"AC_V1V3_9",
	29:"AC_V1V3_10",30:"AC_V2V1_1", 32:"AC_V2V1_2", 33:"AC_V2V1_3", 34:"AC_V2V1_4",
	35:"AC_V2V1_5", 36:"AC_V2V1_6", 38:"AC_V2V1_7", 39:"AC_V2V1_8", 40:"AC_V2V1_9",
	43:"AC_V2V1_10",44:"AC_V3V1_1", 45:"AC_V3V1_2", 46:"AC_V3V1_3", 47:"AC_V3V1_4",
	48:"AC_V3V1_5", 49:"AC_V3V1_6", 50:"AC_V3V1_7", 51:"AC_V3V1_8", 52:"AC_V3V1_9",
	53:"AC_V3V1_10"}

pprz_processes = []




class Aircraft():

	def __init__(self, env, id, start_time, end_time, route, ivy_interface):
		print("Create AC with id = %s, start_time = %s, end_time = %s, and route = %s" % (id, start_time, end_time, route))
		self.env = env
		self.action = env.process(self.run())
		self.id = id
		self.start_time = utils.to_sec(start_time)
		self.end_time = utils.to_sec(end_time)
		self.route = route
		self.ivy_interface = ivy_interface
		self.ussp = None
		self.ussp_port = None
		self.ussp_flight_id = None
		self.ussp_start_time = None
		self.pprz_id = None
		self.latest_tele_report = None
		self.telemetry_agent = None
		self.flight_over = self.env.event()
		## STATUS ARGUMENTS ##
		self.has_flight_plan_validated = False
		self.has_started = False
		self.has_landed = False
		## ARGUMENTS TO "JUDGE" HOW WELL THE VIMS PERFORMS ##
		self.delay = 0



	def __str__(self):
		return ("AC %s with start_time = %s, end_time = %s, and route = %s" % (self.id, self.start_time, self.end_time, self.route))

	def run(self):
		# wait for start_time - FP_SEND_WINDOW_START
		yield self.env.timeout(self.start_time - FP_SEND_WINDOW_START * 60 - self.env.now)
		print("%s min before take off for " % FP_SEND_WINDOW_START, self.id)

		# get random time between FP_SEND_WINDOW_START and FP_SEND_WINDOW_END min // we can also choose to send flight plan at the same time everytime
		time_to_wait_before_fp_sent = random.randint(0, FP_SEND_WINDOW_START - FP_SEND_WINDOW_END) * 60
		
		# wait for time defined above
		#print("%s waiting for %s sec before sending fp" % (self.id, time_to_wait_before_fp_sent))
		yield self.env.timeout(time_to_wait_before_fp_sent)

		# choose randow ussp in USSP_LIST
		ussp = random.choice(USSP_LIST)
		self.ussp = ussp["id"]
		self.ussp_port = ussp["port"]

		# send fp to ussp
		# one day, add buffer in flight request payload
		print("%s sending fp" % self.id)
		url = "http://localhost:%s/%s/flights" % (str(self.ussp_port), self.ussp)
		payload = json.dumps({
			"start_time":self.start_time,
			"end_time":self.end_time,
			"route":self.route
		})
		response = requests.post(url, data=payload)
		print(response.text)

		# wait for confirmation / modification of start time
		if response.status_code == 200: # always the case until we have a real flight authorisation service
			self.ussp_flight_id = response.json()["id"]
			self.ussp_start_time = response.json()["geometry"]["start_time"]
			self.delay = int(self.ussp_start_time) - int(self.start_time)
			self.has_flight_plan_validated = True

		else:
			print("ERROR THAT SHOULDNT HAPPEN N° 1")

		# wait for start_time
		#print("%s waiting for %s sec to start flight after flight validated by ussp" % (self.id, self.start_time - self.env.now))
		yield self.env.timeout(int(self.ussp_start_time) - self.env.now)

		# send flight start to ussp 
		print("%s sending flight start to ussp" % self.id)
		url = "http://localhost:%s/%s/flights/%s/start_flight" % (self.ussp_port, self.ussp, self.ussp_flight_id)
		response = requests.post(url)
		print(response.text)

		# wait for confirmation (should always be yes for V1)
		if response.status_code == 200:
			self.telemetry_endpoint = response.json()["telemetry_endpoint"]
			print("%s start flight" % self.id)
			self.has_started = True
		else:
			print("ERROR THAT SHOULDNT HAPPEN N° 2")


		if run_with_pprz:
			# assign pprz flight id
			if self.route == "V1V2":
				ac_list = L_AC_V1V2
			elif self.route == "V1V3":
				ac_list = L_AC_V1V3
			elif self.route == "V2V1":
				ac_list = L_AC_V2V1
			else:
				ac_list = L_AC_V3V1

			try:
				self.pprz_id = next(id for id in ac_list.keys() if ac_list[id])
			except StopIteration:
				print("NO AC REMAINING IN L_AC_V3V1")

			ac_list[int(self.pprz_id)] = False
			#print("\n \n PPRZ ID ASSIGNED = ", self.pprz_id)

			# start pprz flight
			print("%s STARTING AC %s IN PPRZ" % (self.id, PPRZ_ID_NAME[self.pprz_id]))
			pro = subprocess.Popen("exec /home/corentin/paparazzi/sw/simulator/pprzsim-launch  -a %s" % PPRZ_ID_NAME[self.pprz_id], 
				shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
			pprz_processes.append(pro.pid)

			# init telemetry
			sub_id = self.ivy_interface.subscribe(self.on_telemetry_received, PprzMessage("ground", "FLIGHT_PARAM"))
			self.telemetry_agent = Telemetry_Agent("http://localhost:%s" % self.ussp_port, self, TELEMETRY_TIMESTEP)
			print("%s STARTING TELE" % self.id)
			self.telemetry_agent.keep_sending = True

			# wait untill end_time (or pprz message that flight is over)
			# yield self.env.timeout(1000)
			# use ground JUMP_TO_BLOCK ac_id block_id
			sub_id_2 = self.ivy_interface.subscribe(self.autopilot, PprzMessage("ground", "NAV_STATUS"))

			# wait for event flight_over
			yield self.flight_over
			print("FLIGHT OVER")

			# stop sending telemetry
			print("%s STOPING TELEMETRY" % self.id)
			self.telemetry_agent.keep_sending = False

			# cancel pprz subscription
			self.ivy_interface.unsubscribe(sub_id)

		else:
			# do simulation of route "by hand"
			# wait for time to complete route / simulate some king of telemetry
			if self.route == "V1V2" or self.route == "V2V1":
				yield self.env.timeout(V1_V2_TIME)
			else:
				yield self.env.timeout(V1_V3_TIME)
			print("%s FLIGHT OVER" % self.id)
			pass

		# send flight_over to ussp
		url = "http://localhost:%s/%s/flights/%s/end_flight" % (self.ussp_port, self.ussp, self.ussp_flight_id)
		response = requests.post(url)
		if response.status_code == 200:
			print("%s SUCCESSFULLY STOPPPED SENDING TELEMETRY" % self.id)
			self.has_landed = True
		else:
			print("ERROR THAT SHOULDNT HAPPEN N° 8")
			print(response.text)

		if run_with_pprz:
			# free pprz ac_id (put back in pool)
			ac_list[int(self.pprz_id)] = True

			# kill pprz process
			print("%s KILLING AC %s IN PPRZ" % (self.id, PPRZ_ID_NAME[self.pprz_id]))
			os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

			# send pprz message to delete ac in pprz
			dele_ac_msg = PprzMessage("ground", "AIRCRAFT_DIE")
			dele_ac_msg["ac_id"] = self.pprz_id
			self.ivy_interface.send(dele_ac_msg)

		else:
			# finish simu, somth do to here ?
			pass


	def on_telemetry_received(self, msg_id, msg):
		if str(self.pprz_id) == str(msg["ac_id"]):
			tele_json = json.dumps({
				"id": self.ussp_flight_id,
				"timestamp": self.env.now,
				"telemetry":{
					"lat": msg["lat"],
					"lon": msg["long"],
					"speed": msg["speed"],
					"alt": msg["alt"],
					"course": msg["course"],
					"heading": msg["heading"],
					}
				})
			self.latest_tele_report = tele_json


	def autopilot(self, msg_id, msg):
		current_block_number = msg["cur_block"]
		if int(current_block_number) == 2: # Holding point, means drone is ready
			msg = PprzMessage("ground", "JUMP_TO_BLOCK")
			msg["ac_id"] = self.pprz_id
			msg["block_id"] = 3 # Start Engine
		elif int(current_block_number) == 3: # Start Engine
			msg = PprzMessage("ground", "JUMP_TO_BLOCK")
			msg["ac_id"] = self.pprz_id
			msg["block_id"] = 4 # Takeoff
		elif int(current_block_number) == 5: # STANDBY (automatic switch from takeoff to standby)
			msg = PprzMessage("ground", "JUMP_TO_BLOCK")
			msg["ac_id"] = self.pprz_id
			msg["block_id"] = 6 # route
		elif int(current_block_number) == 10: # landed
			self.flight_over.succed()
		else:
			return
		self.ivy_interface.send(msg)



def main():

	all_ac = []

	#init ivy interface for comm with pprz
	pprz_message_interface = IvyMessagesInterface("SIMU DSS")

	# init the simu env
	env = simpy.rt.RealtimeEnvironment(initial_time=SIMU_START_TIME, factor=TIMSESTEP, strict=False)

	# read xml file and create ac
	with open("DepartureV1.csv") as file:
		csv_file = csv.reader(file)
		header = next(csv_file)
		for row in csv_file:
			id = row[0]
			start_time = row[1]
			if row[2] == "": # means that V3 is the destination
				end_time = row[3]
				route = "V1V3"
			else:
				end_time = row[2]
				route = "V1V2"
			ac = Aircraft(env, id, start_time, end_time, route, pprz_message_interface)
			all_ac.append(ac)

	with open("DepartureV2.csv") as file:
		csv_file = csv.reader(file)
		header = next(csv_file)
		for row in csv_file:
			id = row[0]
			start_time = row[1]
			end_time = row[2]
			route = "V2V1"
			ac = Aircraft(env, id, start_time, end_time, route, pprz_message_interface)
			all_ac.append(ac)

	with open("DepartureV3.csv") as file:
		csv_file = csv.reader(file)
		header = next(csv_file)
		for row in csv_file:
			id = row[0]
			start_time = row[1]
			end_time = row[2]
			route = "V3V1"
			ac = Aircraft(env, id, start_time, end_time, route, pprz_message_interface)
			all_ac.append(ac)

	# start simu
	try:
		env.run()
		## get delay of all ac and print it ##
		mean_delay, total_delay, number_of_flight_plan_val_ac = utils.compute_mean_delay(all_ac)
		print("\n\nRESULTS:\nMEAN DELAY = %s / WITH TOTAL DELAY = %s AND NB OF AC = %s"\
			% (mean_delay, total_delay, number_of_flight_plan_val_ac))
	except KeyboardInterrupt:
		## get delay of all ac and print it ##
		mean_delay, total_delay, number_of_flight_plan_val_ac = utils.compute_mean_delay(all_ac)
		print("\n\nRESULTS:\nMEAN DELAY = %s / WITH TOTAL DELAY = %s AND NB OF AC = %s"\
			% (mean_delay, total_delay, number_of_flight_plan_val_ac))
	finally: # ensure there are no remaining ac processes runnning in case of interruption
		if run_with_pprz:
			for pid in pprz_processes:
				os.kill(pid, signal.SIGTERM)

	# and that's it, the AC should manage and send the information themselves



if __name__ == '__main__':
	main()