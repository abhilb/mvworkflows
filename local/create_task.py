from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from local.parameteritem import ParameterType

class CreateTask(QDialog):
    """ Widget to create task yaml files """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Task Template")

        # Set the layout of the dialog
        layout = QGridLayout(self)
        self.setLayout(layout)

        # Set the name and desciption of the task
        task_name_label = QLabel("Name")
        task_name_text_edit = QLineEdit()
        layout.addWidget(task_name_label, 0, 0)
        layout.addWidget(task_name_text_edit, 0, 1)

        task_description_label = QLabel("Description")
        task_description_edit = QTextEdit()
        layout.addWidget(task_description_label, 1, 0)
        layout.addWidget(task_description_edit, 2, 0, 1, 2)

        # Set parameters
        task_param_type = QComboBox()
        for param_type in ParameterType:
            task_param_type.addItem(str(param_type))
        task_param_list = QListWidget()
        layout.addWidget(task_param_type, 3, 1)
        layout.addWidget(task_param_list, 4, 0, 1, 2)

        # Set inputs

        # Set properties
        prop_grp_box = QGroupBox("Properties")
        prop_grp_box_layout = QVBoxLayout()
        prop_grp_box_layout.addWidget(QCheckBox("Image Provider"))
        prop_grp_box_layout.addWidget(QCheckBox("String Provider"))
        prop_grp_box_layout.addWidget(QCheckBox("Number Provider"))
        prop_grp_box_layout.addWidget(QCheckBox("Number List Provider"))
        prop_grp_box_layout.addWidget(QCheckBox("Feature Provider"))
        prop_grp_box.setLayout(prop_grp_box_layout)
        layout.addWidget(prop_grp_box, 5, 0, 1, 2)

        # Add button box
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box, 6, 0, 1, 2)

    def accept(self):
        """ Dialog save button """
        super().accept()


    def reject(self):
        """ Dialog save button """
        super().reject()
