#!/usr/bin/env/ python3
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from config import drink_list, pump_config, options
import time
import json

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


"""GPIO Outputs:
    Pump1: 31
    Pump2: 32
    Pump3: 33g
    Pump4: 35
    Pump5: 36
    Pump6: 37
    Pump7: 38
    Pump8: 40"""

class ProgressThread(QThread):
    _progSignal = pyqtSignal(int)
    def __init__(self, runtime):
        super(ProgressThread, self).__init__()
        self.runtime = runtime
    def __del__(self):
        self.wait()
    def run(self):
        for i in range(101):
            time.sleep(self.runtime/100)
            self._progSignal.emit(i)

class PumpThread(QThread):
    _statusSignal = pyqtSignal(str)
    def __init__(self,ings=[], pumps=[], values=[],gpio=[], factor=0):
        super(PumpThread, self).__init__()
        self.ings = ings
        self.pumps = pumps
        self.values = values
        self.gpio = gpio
        self.factor = factor
    def __del__(self):
        self.wait()
    def run(self):
        for ing, pump, value, gpio in zip(self.ings, self.pumps, self.values, self.gpio):
            print(f'Pump {pump}, {ing}, {value}ml. GPIO: {gpio}')
            self._statusSignal.emit(f'PUMPE {pump}: {ing} -- {value}ml')
            GPIO.output(gpio, GPIO.HIGH)
            time.sleep(value * self.factor)
            GPIO.output(gpio, GPIO.LOW)

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('PumpSet.ui', self)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.showMaximized()

        self.change_btn1 = self.findChild(QtWidgets.QPushButton, 'pushButton') 
        self.change_btn1.clicked.connect(lambda: self.change_btn_clicked(1))

        self.change_btn2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2') 
        self.change_btn2.clicked.connect(lambda: self.change_btn_clicked(2))

        self.change_btn3 = self.findChild(QtWidgets.QPushButton, 'pushButton_3') 
        self.change_btn3.clicked.connect(lambda: self.change_btn_clicked(3))

        self.change_btn4 = self.findChild(QtWidgets.QPushButton, 'pushButton_4') 
        self.change_btn4.clicked.connect(lambda: self.change_btn_clicked(4))

        self.change_btn5 = self.findChild(QtWidgets.QPushButton, 'pushButton_5') 
        self.change_btn5.clicked.connect(lambda: self.change_btn_clicked(5))

        self.change_btn6 = self.findChild(QtWidgets.QPushButton, 'pushButton_6') 
        self.change_btn6.clicked.connect(lambda: self.change_btn_clicked(6))

        self.change_btn7 = self.findChild(QtWidgets.QPushButton, 'pushButton_7') 
        self.change_btn7.clicked.connect(lambda: self.change_btn_clicked(7))

        self.change_btn8 = self.findChild(QtWidgets.QPushButton, 'pushButton_8') 
        self.change_btn8.clicked.connect(lambda: self.change_btn_clicked(8))

        self.save_btn = self.findChild(QtWidgets.QPushButton, 'pushButton_9') 
        self.save_btn.clicked.connect(self.save_btn_clicked)


        self.show_pump_sets()

    def show_pump_sets(self):

            self.pump_list = Ui.return_pumps(self)

            self.label1 = self.findChild(QtWidgets.QLabel, 'label1')
            self.label1.setText((self.pump_list[0]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label2')
            self.label1.setText((self.pump_list[1]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label3')
            self.label1.setText((self.pump_list[2]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label4')
            self.label1.setText((self.pump_list[3]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label5')
            self.label1.setText((self.pump_list[4]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label6')
            self.label1.setText((self.pump_list[5]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label7')
            self.label1.setText((self.pump_list[6]['name']).upper())

            self.label1 = self.findChild(QtWidgets.QLabel, 'label8')
            self.label1.setText((self.pump_list[7]['name']).upper())


    def change_btn_clicked(self, number):
        self.pump_win = PumpWindow(number)
        self.pump_win.pump_win_closed.connect(self.show_pump_sets)
        self.pump_win.show()
        print(number)

    def save_btn_clicked(self):
        self.close()

class SizeWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('sizeSet.ui', self)

class PumpWindow(QWidget):
    pump_win_closed = pyqtSignal()
    def __init__(self, number):
        super().__init__()
        uic.loadUi('PumpSelection.ui', self)
        self.number = number
        self.label = self.findChild(QtWidgets.QLabel, 'label')
        self.label.setText(f'Pumpe {self.number}')

        self.pump_list = Ui.return_pumps(self)

        self.deact_btn = self.findChild(QtWidgets.QPushButton, 'deact_btn')
        self.deact_btn.clicked.connect(self.deactivate_pump)

        self.save_btn = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.save_btn.clicked.connect(self.save_pump_selection) 

        self.sel_label = self.findChild(QtWidgets.QLabel, 'label_3')
        self.sel_label.setText(self.pump_list[(number -1)]['name'].upper())

        self.options_list = self.findChild(QtWidgets.QListWidget, 'listWidget')
        self.options_list.itemClicked.connect(self.list_handler)
        index = 0
        for i in options:
            self.options_list.insertItem(index, i.upper())
            index += 1
        self.pump_selection = self.pump_list[(number -1)]['name'].lower()


    def list_handler(self):
        self.sel_label.setText((self.options_list.currentItem().text()).upper())
        self.pump_selection = self.options_list.currentItem().text().lower()

    def deactivate_pump(self):
        self.pump_selection = "none"
        self.save_pump_selection()


    def save_pump_selection(self):
        with open('pump_config.json', 'r') as jsonFile:
            data = json.load(jsonFile)
        data[(self.number - 1)]['name'] = self.pump_selection

        with open('pump_config.json', 'w') as jsonFile:
            json.dump(data, jsonFile)
        jsonFile.close()
        #SettingsWindow.show_pump_sets(self)
        self.pump_win_closed.emit()
        self.close()




class Ui(QtWidgets.QMainWindow):
#-Init---------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        #self.show()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.showMaximized()

        self.action_btn = self.findChild(QtWidgets.QPushButton, 'action_btn') 
        self.action_btn.clicked.connect(self.start_request)
        self.action_btn.pressed.connect(self.action_hold)
        self.action_btn.released.connect(self.action_release)

        self.action_btn.hide()

        self.option_btn = self.findChild(QtWidgets.QPushButton, 'option_btn') 
        self.option_btn.clicked.connect(self.option_btn_pressed)
        self.option_btn.setText('Info...')

        self.option_btn.hide()

        self.toggle_btn = self.findChild(QtWidgets.QPushButton, 'toggle_btn') 
        self.toggle_btn.clicked.connect(self.toggle_menu)

        self.list_widget = self.findChild(QtWidgets.QListWidget, 'list_widget')
        self.list_widget.itemClicked.connect(self.selection_handler)


        self.name_label = self.findChild(QtWidgets.QLabel, 'name_label')
        self.name_label.setText('')

        self.progressbar = self.findChild(QtWidgets.QProgressBar, 'progressBar')
        self.progressbar.setValue(0)

        self.statusbar = self.findChild(QtWidgets.QStatusBar, 'statusbar')

        self.settings_btn = self.findChild(QtWidgets.QPushButton, 'settingsButton') 
        #self.settings_btn.setIcon(QIcon('settings.png'))
        self.settings_btn.clicked.connect(self.settings_btn_clicked)

        self.clean_btn = self.findChild(QtWidgets.QPushButton, 'clean_btn') 
        #self.settings_btn.setIcon(QIcon('settings.png'))
        self.clean_btn.clicked.connect(self.clean_btn_clicked)



        self.pump_list = []
        self.get_pumps()
        self.gpio_init()

        self.manual_mode = False
        self.pumping = False
        self.selected = False
        self.cocktail_number = 0
        self.show_cocktail_list()



    def return_pumps(Self):
        pumps = []
        file = open('pump_config.json')
        data = json.load(file)
        file.close()
        return data

    def get_pumps(self):
        file = open('pump_config.json')
        data = json.load(file)
        self.pump_list= data
        print(self.pump_list)
        file.close()

    def gpio_init(self):
        self.get_pumps()
        for pump in self.pump_list:
            GPIO.setup(pump['GPIO'], GPIO.OUT)
            GPIO.output(pump['GPIO'], GPIO.LOW)
            print(pump['GPIO'])


    def show_cocktail_list(self):
        self.selected = False
        self.list_widget.clear()
        self.manual_mode = False
        self.get_pumps()
        self.pump_names = []
        self.filtered_drinks = []
        for p in self.pump_list:
            self.pump_names.append(p['name'])
        print(self.pump_names)
        index = 0
        for drink in drink_list:
            status = 0
            for ing in drink['ingredients'].keys():
                if ing in self.pump_names:
                    status +=1
            if status == len(drink['ingredients']):
                self.list_widget.insertItem(index, drink['name'].upper())
                self.filtered_drinks.append(drink)
                index += 1
        """index = 0
        for i in drink_list:
            self.list_widget.insertItem(index, i['name'].upper())
            index += 1"""
        self.toggle_btn.setText('Manuell...')
        self.action_btn.setText('START')
        self.name_label.setText('<-- Bitte auswählen')
        self.action_btn.hide()

    def show_manu_list(self):
        self.get_pumps()
        self.selected = False
        self.list_widget.clear()
        self.manual_mode = True
        index = 0
        for pump in self.pump_list:
            self.list_widget.insertItem(index, pump['name'].upper())
            index += 1
        self.toggle_btn.setText('Cocktails...')
        self.name_label.setText('<-- Bitte auswählen')
        self.option_btn.hide()
        self.action_btn.hide()
        self.action_btn.setText('PUSH and HOLD')


    def selection_handler(self):
        self.selected = True
        self.action_btn.show()
        self.name_label.setText((self.list_widget.currentItem().text()).upper())
        if not self.manual_mode:
            self.option_btn.show()

    def start_request(self):
        if not self.manual_mode and self.selected == True:
            try:
                req_box = QMessageBox()
                req_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                req_box.setText((self.list_widget.currentItem().text()).upper())
                req_box.setIcon(QMessageBox.Question)
                req_box.setInformativeText('Starten?')
                ings = []
                for i in self.filtered_drinks[self.list_widget.currentRow()]['ingredients'].keys():
                    ings.append(i)
                message = '\n'.join(ings).upper()
                req_box.setDetailedText(message)
                req_box.exec()
                button = req_box.clickedButton()
                sb = req_box.standardButton(button)
                if sb == QMessageBox.Ok:
                    self.start()
            except AttributeError:
                print("no selection!")

    def hide_buttons(self):
        self.action_btn.hide()
        self.option_btn.hide()
        self.toggle_btn.hide()
    def show_buttons(self):
        self.action_btn.show()
        self.option_btn.show()
        self.toggle_btn.show()

    def start(self):
        if not self.manual_mode and self.selected == True:
            try:
                print(self.list_widget.currentRow(), self.list_widget.currentItem().text())
                self.hide_buttons()
                self.cocktail_number = self.list_widget.currentRow()
                factor = 0.04
                pumps = []
                ings = []
                gpio = []
                values = []
                runtime = 0
                self.get_pumps()
                print(self.pump_list)

                for pump in self.pump_list:
                    if pump['name'] in self.filtered_drinks[self.list_widget.currentRow()]['ingredients'].keys():
                        pumps.append(pump['pump'])
                        gpio.append(pump['GPIO'])
                        values.append(self.filtered_drinks[self.list_widget.currentRow()]['ingredients'][pump['name']])
                        ings.append(pump['name'])

                for value in values:
                    runtime += (value * factor)

                #for value in self.filtered_drinks[self.list_widget.currentRow()]['ingredients'].values():
                #    values.append(value)
                #    runtime += (value * factor)
                #for ing in self.filtered_drinks[self.list_widget.currentRow()]['ingredients'].keys():
                #    ings.append(ing)

                print(pumps)
                print(ings)
                print(gpio)
                print(values)

                
                self.pump_thread = PumpThread(ings, pumps, values, gpio, factor)
                self.pump_thread._statusSignal.connect(self.status_signal)
                self.pump_thread.start()

                self.prog_thread = ProgressThread(runtime)
                self.prog_thread._progSignal.connect(self.progress_signal)
                self.prog_thread.start()
            except AttributeError:
                print("no selection!")

    def progress_signal(self, msg):
        self.progressbar.setValue(int(msg))
        if self.progressbar.value() == 100:
            self.statusbar.showMessage('Fertig', 2000)
            self.progressbar.setValue(0)
            ready = QMessageBox()
            ready.setStandardButtons(QMessageBox.Ok)
            ready.setText(self.list_widget.currentItem().text())
            ready.setInformativeText('Fertig! -- PROST!')
            ready.exec()
            button = ready.clickedButton()
            bt = ready.standardButton(button)
            if bt == QMessageBox.Ok:
                self.show_buttons()

    
    def status_signal(self, msg):
        self.statusbar.showMessage(msg)

    def action_hold(self):
        try:
            if self.manual_mode:
                print(f'pump {self.list_widget.currentRow()} START! -- {self.list_widget.currentItem().text()}')
                self.statusbar.showMessage(f'PUMPE LÄUFT! -- {self.list_widget.currentItem().text()}')
                print(self.pump_list[self.list_widget.currentRow()]['GPIO'])
                GPIO.output(self.pump_list[self.list_widget.currentRow()]['GPIO'], GPIO.HIGH)
        except AttributeError:
            print("no selection!")

    def action_release(self):
        try:
            if self.manual_mode:
                GPIO.output(self.pump_list[self.list_widget.currentRow()]['GPIO'], GPIO.LOW)
                print(f'pump {self.list_widget.currentRow()} STOP! -- {self.list_widget.currentItem().text()}')
                self.statusbar.showMessage(f'PUMPE GESTOPPT! -- {self.list_widget.currentItem().text()}', 2000)
        except AttributeError:
            print("no selection!")


    def settings_btn_clicked(self):
        self.w = SettingsWindow()
        self.w.show()

    def size_btn_clicked(self):
        self.size_window = SizeWindow()
        self.size_window.show()

    def clean_btn_clicked(self):
        clean_box = QMessageBox()
        clean_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        clean_box.setText('Reinigen')
        clean_box.setIcon(QMessageBox.Question)
        clean_box.setInformativeText('Starten?')
        clean_box.exec()


    def option_btn_pressed(self):
        ings = []
        for i in self.filtered_drinks[self.list_widget.currentRow()]['ingredients'].keys():
            ings.append(i)
        message = '\n'.join(ings).upper()
        msbx = QMessageBox()
        msbx.setIcon(msbx.Information)
        msbx.setText('Zutaten')
        msbx.setInformativeText(message)
        msbx.exec()


    def show_settings(self):

        pass




    def toggle_menu(self):
        if self.manual_mode:
            self.show_cocktail_list()
            self.name_label.setText('')
        else:
            self.show_manu_list()
            self.name_label.setText('')



app = QtWidgets.QApplication(sys.argv)
window = Ui()

window.show()
app.exec_()
