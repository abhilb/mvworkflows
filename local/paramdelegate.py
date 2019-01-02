from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import logging

from local.parameteritem import *
from local.operatorinfo import OperatorInfo, PROVIDER_TYPE

logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")
logger = logging.getLogger(f"[{__name__}]")

class ParamDelegate(QStyledItemDelegate):
    """
    Delegate for parameter
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        assert(model != None)

        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        parameter_value = parameter.data(Qt.DisplayRole)
        if parameter_type is ParameterType.INT_PARAM:
            editor = QSpinBox(parent)
            editor.setFrame(False)
            editor.setMinimum(3)
            editor.setMaximum(100)
            editor.setValue(int(parameter_value))
            return editor
        elif parameter_type is ParameterType.DOUBLE_PARAM:
            editor = QDoubleSpinBox(parent)
            editor.setFrame(False)
            editor.setMinimum(0)
            editor.setMaximum(10)
            editor.setValue(parameter_value)
            return editor
        elif parameter_type is ParameterType.BOOL_PARAM:
            pass
        elif parameter_type is ParameterType.FILE_PATH_PARAM:
            editor = QFileDialog(parent)
            editor.setFileMode(QFileDialog.Directory)
            return editor
        elif parameter_type is ParameterType.STR_PARAM:
            editor = QLineEdit(parent)
            return editor
        elif parameter_type is ParameterType.INPUT_PARAM:
            editor = QComboBox(parent)

            input_type = parameter.data(Qt.UserRole + 1)
            providers = model.get_providers(input_type)
            for item in providers:
                editor.addItem(item.name, item.id)

            return editor

    def setEditorData(self, editor, index):
        model = index.model()
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        parameter_value = parameter.data(Qt.DisplayRole)
        if parameter_type is ParameterType.INT_PARAM or parameter_type is ParameterType.DOUBLE_PARAM:
            editor.setValue(parameter_value)
        elif parameter_type is ParameterType.BOOL_PARAM:
            pass
        elif parameter_type is ParameterType.FILE_PATH_PARAM:
            pass
        elif parameter_type is ParameterType.STR_PARAM:
            editor.setText(parameter_value)
        elif parameter_type is ParameterType.INPUT_PARAM:
            if parameter_value:
                editor.setCurrentIndex(0)
            else:
                editor.setCurrentIndex(-1)

    def setModelData(self, editor, model, index):
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        if parameter_type is ParameterType.INT_PARAM or parameter_type is ParameterType.DOUBLE_PARAM:
            parameter.setData(editor.value(), Qt.DisplayRole)
        elif parameter_type is ParameterType.BOOL_PARAM:
            pass
        elif parameter_type is ParameterType.FILE_PATH_PARAM:
            selectedFilesList = editor.selectedFiles()
            if selectedFilesList is not None and len(selectedFilesList) > 0:
                selectedFolder = selectedFilesList[0]
                parameter.setData(selectedFolder, Qt.DisplayRole)
        elif parameter_type is ParameterType.STR_PARAM:
            parameter.setData(editor.text(), Qt.DisplayRole)
        elif parameter_type is ParameterType.INPUT_PARAM:
            parameter.setData(editor.currentText(), Qt.DisplayRole)
            parameter.setData(editor.currentData(), Qt.UserRole + 2)

    def updateEditorGeometry(self, editor, option, index):
        model = index.model()
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        if parameter_type != ParameterType.FILE_PATH_PARAM:
            editor.setGeometry(option.rect)

