import sys
from dataclasses import dataclass
from copy import deepcopy

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from enum import Enum, auto

Signal, Slot = pyqtSignal, pyqtSlot


class Cmds(Enum):
    INC = auto()
    DEC = auto()
    NUM = auto()


# This implementation decouples the UI view, model and control classes fairly well.  Downsides to this approach are
# not yet able to have commands that pass data - could use Command pattern or PyQt signals?
# Also need to keep track of three sets of data when adding commands, the list of enums, the map of enum commands to
# functions in the controller and the key mapping.  Might suggest strings and ASCII codes are better than enums and
# PyQt ket codes?

class MainWindow(QMainWindow):
    intSignal = Signal(int)
    
    def __init__(self, button_map):
        super(QMainWindow, self).__init__()

        # Maps to map commands, keys and functions
        self.key_table = {QtCore.Qt.Key_Plus: Cmds.INC, QtCore.Qt.Key_Minus: Cmds.DEC}
        self.key_table.update({k: Cmds.NUM for k in range(QtCore.Qt.Key_0, QtCore.Qt.Key_9+1)})
        print(self.key_table)
        self.func_map = {}

        # Set UI layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        ui_layout = QGridLayout()
        central_widget.setLayout(ui_layout)

        # Create UI elements
        self.display = QLabel()
        ui_layout.addWidget(self.display)

        self.buttons = {}
        for cmd in button_map:
            title = button_map[cmd]
            self.buttons[cmd] = QPushButton(title)
            ui_layout.addWidget(self.buttons[cmd])

            # Need to use this form of lambda to get local copy of button variable
            # otherwise button will be last value in the list for ALL buttons
            # lambda's (or local functions) use value at call time NOT creation!
            # See https://stackoverflow.com/questions/10452770/python-lambdas-binding-to-local-values
            self.buttons[cmd].clicked.connect(lambda state, x=cmd: self.ExecuteCmd(x))

    def ExecuteCmd(self, cmd, data=None):
        """ Takes a command enum code and calls the corresponding function """
        if cmd in self.func_map:
            if data is not None:
                self.func_map[cmd](data)
            else:
                print('No data call')
                self.func_map[cmd]()

    def UpdateDisplay(self, value):
        """ If a change has been made then update the display """
        str_value = str(value)
        self.display.setText(str_value)

    def Connect(self, func_map):
        """ Allows other class (eg model or controller etc) to specify what function to call for each command """
        self.func_map = func_map

    def keyPressEvent(self, event):
        """ Handles key presses."""
        key = event.key()

        if key in self.key_table:
            cmd = self.key_table[key]
            if QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
                num = int(key) - int(QtCore.Qt.Key_0)
                print(key, num, cmd)
                self.ExecuteCmd(cmd, num)
            else:
                self.ExecuteCmd(cmd)


class Controller:
    def __init__(self, _model, _view):
        self.model = _model
        self.view = _view

        self.view.Connect({Cmds.INC: self.Increment, Cmds.DEC: self.Decrement, Cmds.NUM: self.NumberCommand})
        self.view.UpdateDisplay(self.model.value)

    def Increment(self):
        print('Increment called')
        self.model.Increment()
        self.view.UpdateDisplay(self.model.value)

    def Decrement(self):
        print('Decrement called')
        self.model.Decrement()
        self.view.UpdateDisplay(self.model.value)

    def NumberCommand(self, value):
        print(value)


@dataclass
class Model:
    value: int = 0

    def Increment(self):
        self.value += 1

    def Decrement(self):
        self.value -= 1

###############################################################################


def run_app():
    app = QtWidgets.QApplication(sys.argv)

    button_map = {Cmds.INC: '+1', Cmds.DEC: '-1'}

    model = Model()

    main_win = MainWindow(button_map)
    main_win.show()

    control = Controller(model, main_win)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(run_app())
