#!/usr/bin/python3

from PySide6 import QtCore, QtWidgets, QtGui

class ISA_Creation_Dialog(QtWidgets.QDialog):

	def __init__(self):

		super().__init__()

		self.setWindowTitle("CREATE ISA")

		msg = QtWidgets.QLabel("Create custom ISA coming soon, for now its just Toulouse")
		self.line_edit_test = QtWidgets.QLineEdit()
		self.line_edit_test.setText("TOULOUSE")

		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(msg)
		self.layout.addWidget(self.line_edit_test)


	def return_values(self):
		return self.line_edit_test.text()
