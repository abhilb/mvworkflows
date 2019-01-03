"""
Model for Product Explorer Widget
"""
import uuid
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

from local import resources, Operators
from local.product_explorer import ProductExplorer
from local.node import NodeType, NodeItem

def singleton(cls):
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance

class Operator():
    def __init__(self, name, template, wf_id):
        self.__state = {}
        self.__state['name'] = name
        self.__state['type'] = template
        self.__state['id'] = str(uuid.uuid4())
        self.__state['parameters'] = {}
        self.__state['properties'] = []
        self.__state['inputs'] = {}

        self._load_template()

    def _load_template(self):
        """
        Loads the operator template.
        This will update the parameters with default values
        and the inputs and set the properties of the operator
        This is a private function
        """
        try:
            op_template = Operators[self.__state['type']]
            params = {}
            for param in op_template['parameters']:
                params[param['parameter']] = param['value']
            self.__state['parameters'] = params

        except:
            assert("Failed to load the operator template")

    def __str__(self):
        return self.__state

    @property
    def id(self):
        return self._id

class Workflow():
    def __init__(self, name):
        self._id = uuid.uuid4()
        self._name = name
        self._operators = []

    def __str__(self):
        wf_str = f"""
            name: {self._name}
            id = {self._id}
        """
        for op in self._operators:
            wf_str.append(op)
        return wf_str

    @property
    def id(self):
        return self._id

@singleton
class Product():
    __workflows = []
    __metadata = {}

    def __str__(self):
        product_str = f"""
        name = {self.__metadata['name']}
        """
        for wf in __workflows:
            product_str.append(str(wf))
        return product_str

    @property
    def name(self):
        return self._name

    def add_workflow(self, wf):
        self.__workflows.append(wf)

    def del_workflow(self, wf_id):
        for wf in self.__workflows:
            if wf.id == wf_id:
                self.__workflows.remove(wf)
                break
        else:
            logger.warning(f"Workflow with id : {wf_id} is not found in product")


class ProductExplorerModel(QStandardItemModel):
    """
    Model for Product explorer widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._product = Product()
        self.root = QStandardItem("Product")
        self.appendRow(self.root)

    def add_workflow(self, wf_name):
        self._product.add_workflow(Workflow(wf_name))
        wf_node = NodeItem(wf_name, QIcon(":icons/workflow.png"), NodeType.WORKFLOW)
        self.root.appendRow(wf_node)

    def add_operator(self, index, op_name, op_type):
        wf_node = self.itemAtIndex(index)
        wf_node.appendRow(QStandardItem(QIcon(":/icons/operator.png"), op_name))


if __name__ == "__main__":
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    import sys

    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    widget = QWidget()
    layout = QVBoxLayout()
    widget.setLayout(layout)

    view = ProductExplorer()
    view.setModel(ProductExplorerModel())
    view.workflow_selected.connect(lambda index: view.model().add_operator(index, "op", "test"))
    model = view.model()
    model.add_workflow("Test")

    addWorkflowBtn = QPushButton("Add Workflow")
    addOperatorBtn = QPushButton("Add Operator")
    addWorkflowBtn.clicked.connect(lambda: model.add_workflow("workflow"))

    layout.addWidget(view)
    layout.addWidget(addWorkflowBtn)
    layout.addWidget(addOperatorBtn)

    mainWindow.setCentralWidget(widget)
    mainWindow.show()

    sys.exit(app.exec_())
