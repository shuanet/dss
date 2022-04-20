#!/usr/bin/python3


from PySide6 import QtCore, QtWidgets, QtGui


class Sub_Item(QtWidgets.QWidget):

	def __init__(self, sub_id, sub_name, isas):

		super().__init__()

		self._layout = QtWidgets.QGridLayout()
		self.setLayout(self._layout)

		self._sub_id_label = QtWidgets.QLabel('ID : ')
		self._sub_name_label = QtWidgets.QLabel('NAME : ')
		self._isas_label = QtWidgets.QLabel('ISAS : ')
		self.sub_id_label = QtWidgets.QLabel(sub_id)
		self.sub_name_label = QtWidgets.QLabel(sub_name)
		self.isas_label = QtWidgets.QLabel(str(isas))

		self._layout.addWidget(self._sub_id_label, 0, 0)
		self._layout.addWidget(self._sub_name_label, 1, 0)
		self._layout.addWidget(self._isas_label, 2, 0)
		self._layout.addWidget(self.sub_id_label, 0, 1)
		self._layout.addWidget(self.sub_name_label, 1, 1)
		self._layout.addWidget(self.isas_label, 2, 1)	