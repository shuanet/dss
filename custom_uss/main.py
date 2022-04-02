#!/usr/bin/python3


from custom_uss import USSP
import requests
import re

"""
commands:
create_ussp id port 

get_isa isa_id
create_isa toulouse
create_isa name geometry time_start time_end
submit_isa isa_id/isa_name
delete_isa isa_id/isa_name

get_sub sub_id 
create_sub toulouse
create_sub name geometry time_start time_end
submit_sub sub_id/sub_name 
delete_sub sub_id/sub_name

assign_flight flight_id isa_id/isa_name
"""

def is_uuid(uuid):
	match = re.match('[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}', uuid)
	if match is None:
		return False
	else:
		return True




def main():

	loop_ussp_init = True
	while loop_ussp_init:
		cmd_create_ussp = input()
		cmd_create_ussp_args = re.split(r'\s', cmd_create_ussp)
		if cmd_create_ussp_args[0] == "create_ussp" \
		and isinstance(cmd_create_ussp_args[1], str) \
		and int(cmd_create_ussp_args[2]) < 9999 \
		and int(cmd_create_ussp_args[2]) >= 1000:
			ussp = USSP(cmd_create_ussp_args[1], cmd_create_ussp_args[2])
			ussp.authentify_read()
			ussp.authentify_write()
			loop_ussp_init = False
		else:
			print('bad cmd, use create_ussp id port')

	while True:
		try:
			cmd = input('\n')
			cmd_args = re.split(r'\s', cmd)
			if cmd_args[0] == "create_isa":
				if cmd_args[1] == 'toulouse':
					ussp.create_isa_test()
				else:
					ussp.create_isa(cmd_args[1], cmd_args[2], cmd_args[3], cmd_args[4])
			elif cmd_args[0] == "submit_isa":
				if is_uuid(cmd_args[1]):
					ussp.submit_isa(_isa_id=cmd_args[1]) # TODO manage if no id submit last isa created
				else:
					ussp.submit_isa(_isa_name=cmd_args[1])
			elif cmd_args[0] == "get_isa":
				ussp.get_isa(cmd_args[1])
			elif cmd_args[0] == "delete_isa": 
				if is_uuid(cmd_args[1]):
					ussp.delete_isa(_isa_id=cmd_args[1])
				else:
					ussp.delete_isa(_isa_name=cmd_args[1])
			elif cmd_args[0] == "create_sub":
				if cmd_args[1] == "toulouse":
					ussp.create_subscription_test()
				else:
					ussp.create_subscription(cmd_args[1], cmd_args[2], cmd_args[3], cmd_args[4])
			elif cmd_args[0] == "submit_sub":
				if is_uuid(cmd_args[1]):
					ussp.submit_subscription(_sub_id=cmd_args[1]) # TODO manage if no id submit last sub created
				else:
					ussp.submit_subscription(_sub_name=cmd_args[1])
			elif cmd_args[0] == "get_sub":
				ussp.get_subscription(_sub_id=cmd_args[1])
			elif cmd_args[0] == "delete_sub":
				if is_uuid(cmd_args[1]):
					ussp.delete_subscription(_sub_id=cmd_args[1])
				else:
					ussp.delete_subscription(_sub_name=cmd_args[1])
			else:
				print("unknown cmd %s" % cmd_args[0])
		except KeyboardInterrupt:
			# delete all ISAs created 
			print("Deleting ISAs before killing ussp")
			for isa in ussp.isas:
				ussp.delete_isa(_isa_id=isa.id)
			# delete all subs created
			print("Deleting subs before killing ussp")
			for sub in ussp.subscriptions:
				ussp.delete_subscription(_sub_id=sub.id)
			print("Done")
			return


if __name__ == "__main__":
	main()