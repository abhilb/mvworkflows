from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from enum import Enum

class ParameterType(Enum):
    INT_PARAM = 1
    DOUBLE_PARAM = 2
    BOOL_PARAM = 3
    FILE_PATH_PARAM = 4
    STR_PARAM = 5

class ParameterItem(QStandardItem):
    """
    Inherits QStandardItem
    Represents different types of parameters
    """
    def __init__(self, param_type, param_value, parent=None):
        super().__init__(parent)
        self.param_type = param_type
        self.param_value = param_value
        self.param_default_value = param_value
        self.setData(self.param_value, Qt.DisplayRole)

    def get_param_type(self):
        return self.param_type

    def get_param_value(self):
        return self.param_value

    def set_param_value(self, param_value):
        self.param_value = param_value
        self.setData(self.param_value, Qt.DisplayRole)

    def get_param_default_value(self):
        return self.param_default_value

    def set_param_default_value(self, default_value):
        self.param_default_value = default_value
