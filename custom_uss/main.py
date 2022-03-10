#!/usr/bin/python3


from custom_uss import USSP
import requests
import re

"""
commands:
create_ussp id port

create_isa toulouse
create_isa name geometry time_start time_end
submit_isa isa_id
delete_isa isa_id

create_sub toulouse
create_sub name geometry time_start time_end
submit_sub sub_id
delete_sub isa_id

"""


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
			cmd = input()
			cmd_args = re.split(r'\s', cmd)
			if cmd_args[0] == "create_isa":
				if cmd_args[1] == 'toulouse':
					ussp.create_isa_test()
				else:
					ussp.create_isa(cmd_args[1], cmd_args[2], cmd_args[3], cmd_args[4])
			elif cmd_args[0] == "submit_isa":
				ussp.submit_isa(cmd_args[1]) # TODO manage if no id submit last isa created
			elif cmd_args[0] == "get_isa":
				ussp.get_isa(cmd_args[1]) # TODO allow to get isa by name
			elif cmd_args[0] == "delete_isa": 
				ussp.delete_isa(cmd_args[1]) # TODO allow to delete isas by name and not id
			elif cmd_args[0] == "create_sub":
				if cmd_args[1] == "toulouse":
					ussp.create_subscription_test()
				else:
					ussp.create_subscription(cmd_args[1], cmd_args[2], cmd_args[3], cmd_args[4])
			elif cmd_args[0] == "submit_sub":
				ussp.submit_subscription(cmd_args[1]) # TODO manage if no id submit last sub created
			elif cmd_args[0] == "get_sub":
				ussp.get_subscription(cmd_args[1]) # TODO allow to get sub by name
			elif cmd_args[0] == "delete_sub":
				ussp.delete_sbscription(cmd_args[1]) # TODO allow to delete subs by name
			else:
				print("unknown cmd %s" % cmd_args[0])
		except KeyboardInterrupt:
			# delete all ISAs created 
			print("Deleting ISAs before killing ussp")
			for isa in ussp.isas:
				ussp.delete_isa(isa.id)
			print("Done")
			return


if __name__ == "__main__":
	main()