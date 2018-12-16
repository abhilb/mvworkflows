from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

from local.parameteritem import *

class ParamDelegate(QStyledItemDelegate):
    """
    Delegate for parameter
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.info("Param delegate created")

    def createEditor(self, parent, option, index):
        model = index.model()
        assert(model != None)
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        parameter_value = parameter.data(Qt.DisplayRole)
        print(f"Parameter type: {parameter_type} - {type(parameter_type)}")
        if parameter_type is ParameterType.INT_PARAM:
            editor = QSpinBox(parent)
            editor.setFrame(False)
            editor.setMinimum(3)
            editor.setMaximum(100)
            editor.setValue(int(parameter_value))
            return editor
        else:
            return QPushButton("Test")

    def setEditorData(self, editor, index):
        model = index.model()
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        parameter_value = parameter.data(Qt.DisplayRole)
        if parameter_type is ParameterType.INT_PARAM:
            editor.setValue(int(parameter_value))

    def setModelData(self, editor, model, index):
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        if parameter_type is ParameterType.INT_PARAM:
            parameter.setData(editor.value(), Qt.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
