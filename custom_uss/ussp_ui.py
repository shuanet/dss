#!/usr/bin/python3

import sys

from PySide6 import QtCore, QtWidgets, QtGui

from custom_uss import USSP

from custom_widgets.outlog import OutLog
from custom_widgets.flight_list_item import Flight_Item
from custom_widgets.isa_list_item import ISA_Item
from custom_widgets.sub_list_item import Sub_Item

from custom_widgets.isa_creation_dialog import ISA_Creation_Dialog


class USSP_UI(QtWidgets.QWidget):


	def __init__(self):

		## GLOBAL VARIABLES ##
		self.ussp = None

		super().__init__()

		self.setWindowTitle("USSP UI")
		self.resize(1500, 950)
		self._layout = QtWidgets.QVBoxLayout(self)

		# main box
		self.main_box = QtWidgets.QGroupBox('')
		self._layout.addWidget(self.main_box)
		self.main_layout = QtWidgets.QGridLayout()
		self.main_box.setLayout(self.main_layout)

		# top left box box
		self.top_box = QtWidgets.QGroupBox('')
		self.top_box.setFixedWidth(400)
		self.main_layout.addWidget(self.top_box, 0, 0)
		self.top_box.setFixedHeight(120)
		self.top_box_layout = QtWidgets.QGridLayout()
		self.top_box.setLayout(self.top_box_layout)
		# top box widgets
		self.id_label = QtWidgets.QLabel('USSP ID')
		self.port_label = QtWidgets.QLabel('http://localhost:')
		self.id_line_edit = QtWidgets.QLineEdit()
		self.id_line_edit.setFixedWidth(100)
		self.port_line_edit = QtWidgets.QLineEdit()
		self.port_line_edit.setFixedWidth(100)
		self.start_ussp_button = QtWidgets.QPushButton('START USSP')
		self.start_ussp_button.setFixedWidth(100)
		self.start_ussp_button.clicked.connect(self.on_start_ussp_clicked)
		self.stop_ussp_button = QtWidgets.QPushButton('STOP USSP')
		self.stop_ussp_button.setFixedWidth(100)
		self.stop_ussp_button.clicked.connect(self.on_stop_ussp_clicked)
		self.auth_read_label = QtWidgets.QLabel('auth read : ')
		self.auth_write_label = QtWidgets.QLabel('auth write : ')
		self.auth_write_status_label = QtWidgets.QLabel('NO')
		self.auth_read_status_label = QtWidgets.QLabel('NO')
		# add widgets to layout
		self.top_box_layout.addWidget(self.id_label, 0, 0)
		self.top_box_layout.addWidget(self.port_label, 1, 0)
		self.top_box_layout.addWidget(self.id_line_edit, 0, 1)
		self.top_box_layout.addWidget(self.port_line_edit, 1, 1)
		self.top_box_layout.addWidget(self.start_ussp_button, 2, 0, 1, 2)
		self.top_box_layout.addWidget(self.auth_read_label, 0, 2)
		self.top_box_layout.addWidget(self.auth_read_status_label, 0, 3)
		self.top_box_layout.addWidget(self.auth_write_label, 1, 2)
		self.top_box_layout.addWidget(self.auth_write_status_label, 1, 3)
		self.top_box_layout.addWidget(self.stop_ussp_button, 2, 2, 1, 2)

		# top right box
		self.top_right_box = QtWidgets.QGroupBox()
		self.main_layout.addWidget(self.top_right_box, 0, 1)
		self.top_right_box_layout = QtWidgets.QGridLayout()
		self.top_right_box.setLayout(self.top_right_box_layout)
		# top right box widgets
		self.request_method_combo_box = QtWidgets.QComboBox()
		self.request_method_combo_box.addItems(['GET', 'PUT', 'POST', 'DEL'])
		self.url_line_edit = QtWidgets.QLineEdit()
		self.url_line_edit.setText('http://localhost:')
		self.read_headers_checkbox = QtWidgets.QCheckBox('read headers')
		self.write_headers_checkbox = QtWidgets.QCheckBox('write headers')
		self.payload_checkbox = QtWidgets.QCheckBox('payload')
		self.payload_text_edit = QtWidgets.QTextEdit()
		self.payload_text_edit.setText('payload = {}')
		self.send_request_button = QtWidgets.QPushButton('SEND')
		self.send_request_button.clicked.connect(self.on_send_request_button_clicked)
		# add widgets to layout
		self.top_right_box_layout.addWidget(self.request_method_combo_box, 1, 0)
		self.top_right_box_layout.addWidget(self.url_line_edit, 1, 1)
		self.top_right_box_layout.addWidget(self.read_headers_checkbox, 0, 2)
		self.top_right_box_layout.addWidget(self.write_headers_checkbox, 1, 2)
		self.top_right_box_layout.addWidget(self.payload_checkbox, 2, 2)
		self.top_right_box_layout.addWidget(self.payload_text_edit, 0, 3, 3, 1)
		self.top_right_box_layout.addWidget(self.send_request_button, 1, 4)

		# middle box
		self.middle_box = QtWidgets.QGroupBox('')
		self.main_layout.addWidget(self.middle_box, 1, 0, 1, 2)
		self.middle_box_layout = QtWidgets.QHBoxLayout()
		self.middle_box.setLayout(self.middle_box_layout)

		# flight box
		self.flight_box = QtWidgets.QGroupBox('FLIGHTS')
		self.flight_box.setFixedWidth(450)
		self.middle_box_layout.addWidget(self.flight_box)
		self.flight_box_layout = QtWidgets.QGridLayout()
		self.flight_box.setLayout(self.flight_box_layout)
		# flight box widgets
		self.flight_list = QtWidgets.QListWidget()
		self.flight_list.itemClicked.connect(self.on_flight_clicked)
		self.accept_flight_button = QtWidgets.QPushButton('ACCEPT')
		self.accept_flight_button.clicked.connect(self.on_accept_flight_button_clicked)
		self.assign_isa_button = QtWidgets.QPushButton('ASSIGN ISA')
		self.assign_isa_button.clicked.connect(self.on_assign_isa_button_clicked)
		self.remove_flight_button = QtWidgets.QPushButton('REMOVE')
		self.remove_flight_button.clicked.connect(self.on_remove_flight_button_clicked)
		# add widgets to layout
		self.flight_box_layout.addWidget(self.flight_list, 0, 0, 1, 3)
		self.flight_box_layout.addWidget(self.accept_flight_button, 1, 0)
		self.flight_box_layout.addWidget(self.assign_isa_button, 1, 1)
		self.flight_box_layout.addWidget(self.remove_flight_button, 1, 2)
		## FOR TESTING PURPOSES : TO DELETE WHEN READY ##
		flight_item = Flight_Item('1234', '4567', 'ON_FLIGHT')
		flight_item_widget = QtWidgets.QListWidgetItem(self.flight_list)
		flight_item_widget.setSizeHint(flight_item.sizeHint())
		self.flight_list.addItem(flight_item_widget)
		self.flight_list.setItemWidget(flight_item_widget, flight_item)

		# isa box
		self.isa_box = QtWidgets.QGroupBox('ISAs')
		self.isa_box.setFixedWidth(450)
		self.middle_box_layout.addWidget(self.isa_box)
		self.isa_box_layout = QtWidgets.QGridLayout()
		self.isa_box.setLayout(self.isa_box_layout)
		# isa widgets
		self.isa_list = QtWidgets.QListWidget()
		self.isa_list.itemClicked.connect(self.on_isa_clicked)
		self.create_isa_button = QtWidgets.QPushButton('CREATE ISA')
		self.create_isa_button.clicked.connect(self.on_create_isa_button_clicked)
		self.update_isa_button = QtWidgets.QPushButton('UPDATE ISA')
		self.update_isa_button.clicked.connect(self.on_update_isa_button_clicked)
		self.delete_isa_button = QtWidgets.QPushButton('DELETE ISA')
		self.delete_isa_button.clicked.connect(self.on_delete_isa_button_clicked)
		# add widgets to layout
		self.isa_box_layout.addWidget(self.isa_list, 0, 0, 1, 3)
		self.isa_box_layout.addWidget(self.create_isa_button, 1, 0)
		self.isa_box_layout.addWidget(self.update_isa_button, 1, 1)
		self.isa_box_layout.addWidget(self.delete_isa_button, 1, 2)

		# sub box
		self.sub_box = QtWidgets.QGroupBox('SUBSCRIPTIONS')
		self.middle_box_layout.addWidget(self.sub_box)
		self.sub_box_layout = QtWidgets.QGridLayout()
		self.sub_box.setLayout(self.sub_box_layout)
		# sub widgets
		self.sub_list = QtWidgets.QListWidget()
		self.sub_list.itemClicked.connect(self.on_sub_clicked)
		self.create_sub_button = QtWidgets.QPushButton('CREATE SUB')
		self.create_sub_button.clicked.connect(self.on_create_sub_button_clicked)
		self.update_sub_button = QtWidgets.QPushButton('UPDATE SUB')
		self.update_sub_button.clicked.connect(self.on_update_sub_button_clicked)
		self.delete_sub_button = QtWidgets.QPushButton('DELETE SUB')
		self.delete_sub_button.clicked.connect(self.on_delete_sub_button_clicked)
		# add widgets to layout
		self.sub_box_layout.addWidget(self.sub_list, 0, 0, 1, 3)
		self.sub_box_layout.addWidget(self.create_sub_button, 1, 0)
		self.sub_box_layout.addWidget(self.update_sub_button, 1, 1)
		self.sub_box_layout.addWidget(self.delete_sub_button, 1, 2)
		# FOR TESTING PURPOSES : TO DELETE WHEN READY ##
		sub_item = Sub_Item('1234', 'toulouse', ['isa.1234', 'isa.5678'])
		sub_item_widget = QtWidgets.QListWidgetItem(self.sub_list)
		sub_item_widget.setSizeHint(sub_item.sizeHint())
		self.sub_list.addItem(sub_item_widget)
		self.sub_list.setItemWidget(sub_item_widget, sub_item)

		# bottom box - outlog
		self.out_log = QtWidgets.QTextEdit()
		self.out_log.setFixedHeight(150)
		self.font = QtGui.QFont()
		self.font.setPointSize(8)
		self.out_log.setFont(self.font)
		self._layout.addWidget(self.out_log)
		sys.stdout = OutLog(self.out_log, sys.stdout)
		sys.stderr = OutLog(self.out_log, sys.stderr)



	def on_start_ussp_clicked(self):
		print("START USSP CLICKED")
		# get ID & port
		ussp_id = self.id_line_edit.text()
		port = self.port_line_edit.text()
		print(ussp_id, port)
		# create USSP 
		self.ussp = USSP(ussp_id, port)
		# authentify for read and write
		status_code_read = self.ussp.authentify_read()
		status_code_write = self.ussp.authentify_write()
		# update read and write labels in UI
		if status_code_read == 200:
			self.auth_read_status_label.setText("YES")
		if status_code_write == 200:
			self.auth_write_status_label.setText("YES")
		return


	def on_stop_ussp_clicked(self):
		print("STOP USSP CLICKED")
		del self.ussp
		return


	def on_flight_clicked(self, item):
		print("FLIGHT CLICKED")
		return


	def on_accept_flight_button_clicked(self):
		print("ACCEPT FLIGHT CLICKED WITH FLIGHT %s" % self.flight_list.selectedItems())
		return 


	def on_assign_isa_button_clicked(self):
		print("ASSIGN ISA CLICKED WITH FLIGHT %s" % self.flight_list.selectedItems())
		return


	def on_remove_flight_button_clicked(self):
		print("REMOVE FLIGHT CLICKED WITH FLIGHT %s" % self.flight_list.selectedItems())
		return


	def on_isa_clicked(self, item):
		print("ISA CLICKED")
		isa_id = self.isa_list.itemWidget(item).isa_id_label.text()
		isa = next(isa for isa in self.ussp.isas if str(isa.id) == str(isa_id))
		print(isa)
		return


	def on_create_isa_button_clicked(self):
		print("CREATE ISA CLICKED")
		dialog = ISA_Creation_Dialog()
		dialog.exec()
		return_val = dialog.return_values()
		print(return_val)
		if return_val == "TOULOUSE":
			print("CREATE ISA TLS")
			self.ussp.create_isa_test()
		self.update_isa_list()
		return


	def on_update_isa_button_clicked(self):
		print("UPDATE ISA CLICKED")
		print("NOT SUPPORTED YET")
		return


	def on_delete_isa_button_clicked(self):
		print("DELETE ISA CLICKED")
		return


	def on_sub_clicked(self, item):
		print("SUB CLICKED")
		return


	def on_create_sub_button_clicked(self):
		print("CREATE SUB CLICKED")
		return


	def on_update_sub_button_clicked(self):
		print("UPDATE SUB CLICKED")
		return


	def on_delete_sub_button_clicked(self):
		print("DELETE SUB CLICKED")
		return


	def on_send_request_button_clicked(self):
		print("SEND REQUEST CLICKED")
		return


	## UI FONCTIONS ##

	def update_isa_list(self):
		self.isa_list.clear()
		for isa in self.ussp.isas:
			isa_item = ISA_Item(isa, self.ussp.id)
			isa_item_widget = QtWidgets.QListWidgetItem(self.isa_list)
			isa_item_widget.setSizeHint(isa_item.sizeHint())
			self.isa_list.addItem(isa_item_widget)
			self.isa_list.setItemWidget(isa_item_widget, isa_item)




if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	ui = USSP_UI()
	ui.show()
	sys.exit(app.exec())