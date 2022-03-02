#!/usr/bin/python3


from custom_uss import USSP


def main():

	print("Starting USSPs")
	ussp1 = USSP('ussp1', 8094)
	ussp2 = USSP('ussp2', 8091)
	ussp1.authentify_read()
	ussp1.authentify_write()
	ussp2.authentify_read()
	#ussp2.authentify_write()
	isa_id = ussp1.create_isa()
	ussp2.get_isa(_isa_id=isa_id)
	ussp2.subscribe()


if __name__ == "__main__":
	main()