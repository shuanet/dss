#!/usr/bin/python3


from PySide6 import QtCore, QtWidgets, QtGui


class Flight_Item(QtWidgets.QWidget):

	def __init__(self, flight_id, isa_id, status):

		super().__init__()

		self._layout = QtWidgets.QGridLayout()
		self.setLayout(self._layout)

		self._flight_label = QtWidgets.QLabel('FLIGHT : ')
		self._ISA_label = QtWidgets.QLabel('ISA : ')
		self._status_label = QtWidgets.QLabel('STATUS : ')
		self.flight_id_label = QtWidgets.QLabel(flight_id)
		self.isa_id_label = QtWidgets.QLabel(isa_id)
		self.status_label = QtWidgets.QLabel(status)

		self._layout.addWidget(self._flight_label, 0, 0)
		self._layout.addWidget(self._ISA_label, 1, 0)
		self._layout.addWidget(self._status_label, 2, 0)
		self._layout.addWidget(self.flight_id_label, 0, 1)
		self._layout.addWidget(self.isa_id_label, 1, 1)
		self._layout.addWidget(self.status_label, 2, 1)

