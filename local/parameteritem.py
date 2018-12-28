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
    INPUT_PARAM = 100

