#!/usr/bin/python3



class ISA():
<<<<<<< HEAD
	"""
	Deine an ISA's attributes.
	"""
	def __init__(self, _name, _id, _geometry, _time_start, _time_end):
=======

	def __init__(self, _name, _id, _geometry, _time_start, _time_end, _owner):
>>>>>>> 8390865225a9ee0052e5d946beb76e3b4c53f8dd

		self.name = _name
		self.id = _id
		self.geometry = _geometry
		self.time_start = _time_start
		self.time_end = _time_end
		self.owner = _owner
		self.submitted = False


	def __str__(self):
		return "ISA: %s \n ID:%s \n GEOMETRY:%s \n TIME_START:%s \n TIME_END:%s " \
		% (self.name, self.id, self.geometry, self.time_start, self.time_end)

