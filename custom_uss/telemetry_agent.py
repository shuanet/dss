#!/usr/bin/python3


import threading
import asyncio
import websockets
import socketio

import time


class Telemetry_Agent():


	def __init__(self, url, parent, timestep):

		self.url = url
		self.parent = parent
		self.timestep = timestep
		self.keep_sending = False

		self.sio = socketio.Client()

		self.thread_server = threading.Thread(target=self.run_tele_thread, daemon=True)
		self.thread_server.start()


	def run_tele_thread(self):
		self.sio.connect(self.url)
		while self.keep_sending:
			time.sleep(self.timestep)
			if self.parent.latest_tele_report is None:
				return
			self.sio.emit('TELEMETRY', self.parent.latest_tele_report)
		
