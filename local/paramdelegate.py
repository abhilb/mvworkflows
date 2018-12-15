from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

class ParamDelegate(QStyledItemDelegate):
    """
    Delegate for parameter
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("Param delegate created")

    def createEditor(self, parent, option, index):
        logging.info("Create editor called")
        pass

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, model, index):
        pass

    def updateEditorGeometry(self, editor, option, index):
        pass
