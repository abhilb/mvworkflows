from enum import Enum
from PyQt5.QtGui import QStandardItem

class NodeType(Enum):
    WORKFLOW=1
    OPERATOR=2
    PRODUCT=3
    OPERATORINFO=4
    UNKNOWN=100

class NodeItem(QStandardItem):
    def __init__(self, name, icon, node_type=NodeType.UNKNOWN):
        super().__init__(icon, name)
        self.node_type = node_type

