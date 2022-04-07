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
			if cmd_args[0] == "get_vertiport":
				vims.get_vertiport(cmd_args[1])
		
		except KeyboardInterrupt:
			# delete all ISAs created 
			print("Deleting Vertiports before killing VIMS")
			for vertiport in vims.vertiports:
				vims.delete_vertiport(_vertiport_name=vertiport.name)
			print("Done")
			return

if __name__ == "__main__":
	main()