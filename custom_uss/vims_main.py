#!/usr/bin/python3

import re
from custom_vims import VIMS
import json

"""
commands:
$ create_vims id port
$ create_vertiport ENAC
$ create_vertiport LFBO

$ get_vertiport vertiport_name
$ delete_vertiport vertiport_name
"""

def is_uuid(uuid):
	"""
	UUID encription.
	"""
	match = re.match('[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}', uuid)
	if match is None:
		return False
	else:
		return True

def create_vertiport_test_ENAC(self):
	"""
	Create a predetermined Vertiport "ENAC" for testing.
	"""
	f = open("ENAC_Vertiport.json", "r")
	data = json.load(f)
	print(data)

	_vertiport_id = uuid.uuid1()
	_time_start = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
	_time_end = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

	vertiport = Vertiport(_vertiport_id, data[1], data[3], data[4], data[5], data[6], _time_start, _time_end, data[9], data[10], data[11], data[12], data[13])
	self.vertiports.append(vertiport)

	print("Vertiport created with id: %s" % _vertiport_id)
	print(vertiport)


def create_vertiport_test_LFBO(self, ):
	"""
	Create a predetermined Vertiport "LFBO" for testing.
	"""
	f = open("LFBO_Vertiport.json", "r")
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

def main():	
	"""
	Main program.
	"""
	loop_vims_init = True
	while loop_vims_init:
		cmd_create_vims = input()
		cmd_create_vims_args = re.split(r'\s', cmd_create_vims)
		if cmd_create_vims_args[0] == "create_vims" \
		and isinstance(cmd_create_vims_args[1], str) \
		and int(cmd_create_vims_args[2]) < 9999 \
		and int(cmd_create_vims_args[2]) >= 1000:
			vims = VIMS(cmd_create_vims_args[1], cmd_create_vims_args[2])
			vims.authentify_read()
			vims.authentify_write()
			loop_vims_init = False
		else:
			print('bad cmd, use $ create_vims id port')

	while True:
		try:
			cmd = input('\n')
			cmd_args = re.split(r'\s', cmd)
			if cmd_args[0] == "create_vertiport":
				if cmd_args[1] == 'ENAC':
					vims.create_vertiport_test_ENAC()
				if cmd_args[1] == 'LFBO':
					vims.create_vertiport_test_LFBO()
			elif cmd_args[0] == "get_vertiport":
				vims.get_vertiport(cmd_args[1])
			elif cmd_args[0] == "delete_vertiport": 
				vims.delete_vertiport(_vertiport_name=cmd_args[1])
		
		except KeyboardInterrupt:
			# delete all ISAs created 
			print("Deleting Vertiports before killing VIMS")
			for vertiport in vims.vertiports:
				vims.delete_vertiport(_vertiport_name=vertiport.name)
			print("Done")
			return

if __name__ == "__main__":	
	main()