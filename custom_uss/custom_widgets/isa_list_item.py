#!/usr/bin/python3


from PySide6 import QtCore, QtWidgets, QtGui


class ISA_Item(QtWidgets.QWidget):

	def __init__(self, isa, owner):

		super().__init__()

		self._layout = QtWidgets.QGridLayout()
		self.setLayout(self._layout)

		self._isa_id_label = QtWidgets.QLabel('ID : ')
		self._isa_name_label = QtWidgets.QLabel('NAME : ')
		self._owner_label = QtWidgets.QLabel('OWNER : ')
		self.isa_id_label = QtWidgets.QLabel(str(isa.id))
		self.isa_name_label = QtWidgets.QLabel(str(isa.name))
		self.owner_label = QtWidgets.QLabel(str(owner))

		self._layout.addWidget(self._isa_id_label, 0, 0)
		self._layout.addWidget(self._isa_name_label, 1, 0)
		self._layout.addWidget(self._owner_label, 2, 0)
		self._layout.addWidget(self.isa_id_label, 0, 1)
		self._layout.addWidget(self.isa_name_label, 1, 1)
		self._layout.addWidget(self.owner_label, 2, 1)		