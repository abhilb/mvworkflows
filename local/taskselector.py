"""
Dialog to select a task type
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class TaskSelector(QDialog):
    """ Widget for selecting tasks """
    def __init__(self, tasks, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 400, 400)

        self.task_description = QTextEdit(self)
        self.task_description.setReadOnly(True)

        self.task_list = QListWidget(self)
        self.task_list.currentRowChanged.connect(self.task_selection_changed)
        self.task_description_list = []

        for _,task_info in tasks.items():
            print(task_info)
            task_list_item = QListWidgetItem(self.task_list)
            task_list_item.setText(task_info['name'])
            if 'description' in task_info.keys():
                self.task_description_list.append(task_info['description'])
            else:
                self.task_description_list.append("documentation not available ")

        if self.task_list.count() > 0:
            self.task_list.setCurrentRow(0)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.task_list)
        self.layout.addWidget(self.task_description)

        self.setLayout(self.layout)

    def task_selection_changed(self):
        currentRow = self.task_list.currentRow()
        if currentRow >= 0:
            self.task_description.setText(self.task_description_list[currentRow])

    def get_selected_task(self):
        currentItem = self.task_list.currentItem()
        if currentItem is None:
            return ""
        else:
            return currentItem.text()
