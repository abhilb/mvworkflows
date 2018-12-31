from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import pyqtSignal, QModelIndex

from local.node import NodeType

class ProductExplorer(QTreeView):
    """ Product explorer widget - inherits QTreeView """

    operator_selected = pyqtSignal(QModelIndex)

    def __init__(self, parent = None):
        super().__init__(parent)

    def set_model(self, model):
        """ Set the model for the product explorer """
        self.setModel(model)
        selectionModel = self.selectionModel()
        selectionModel.currentChanged.connect(self.on_current_changed)

    def on_current_changed(self, index):
        currentIndex = self.selectionModel().currentIndex()
        node = self.model().itemFromIndex(currentIndex)
        if node is not None:
            nodeType = node.node_type
            if nodeType == NodeType.OPERATOR:
                self.operator_selected.emit(index)
