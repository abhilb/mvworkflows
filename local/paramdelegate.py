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
        print(f"parameter type: {parameter_type} - {type(parameter_type)}")
        if parameter_type is ParameterType.INT_PARAM:
            editor = QSpinBox(parent)
            editor.setFrame(False)
            editor.setMinimum(3)
            editor.setMaximum(100)
            editor.setValue(int(parameter_value))
            return editor
        elif parameter_type is ParameterType.BOOL_PARAM:
            editor = QCheckBox(parent)
            return editor
        elif parameter_type is ParameterType.FILE_PATH_PARAM:
            editor = QFileDialog(parent)
            editor.setFileMode(QFileDialog.Directory)
            return editor
        elif parameter_type is ParameterType.STR_PARAM:
            editor = QLineEdit(parent)
            return editor

    def setEditorData(self, editor, index):
        model = index.model()
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        parameter_value = parameter.data(Qt.DisplayRole)
        if parameter_type is ParameterType.INT_PARAM:
            editor.setValue(int(parameter_value))
        elif parameter_type is ParameterType.BOOL_PARAM:
            editor.setChecked(parameter_value)
        elif parameter_type is ParameterType.FILE_PATH_PARAM:
            pass
        elif parameter_type is ParameterType.STR_PARAM:
            editor.setText(parameter_value)

    def setModelData(self, editor, model, index):
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        if parameter_type is ParameterType.INT_PARAM:
            parameter.setData(editor.value(), Qt.DisplayRole)
        elif parameter_type is ParameterType.BOOL_PARAM:
            parameter.setData(editor.isChecked(), Qt.DisplayRole)
        elif parameter_type is ParameterType.FILE_PATH_PARAM:
            selectedFilesList = editor.selectedFiles()
            if selectedFilesList is not None and len(selectedFilesList) > 0:
                selectedFolder = selectedFilesList[0]
                parameter.setData(selectedFolder, Qt.DisplayRole)
        elif parameter_type is ParameterType.STR_PARAM:
            parameter.setData(editor.text(), Qt.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        model = index.model()
        parameter = model.itemFromIndex(index)
        parameter_type = parameter.data(Qt.UserRole)
        if parameter_type != ParameterType.FILE_PATH_PARAM:
            editor.setGeometry(option.rect)

