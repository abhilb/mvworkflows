import json
import glob
import os
import re
import yaml
import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import resources

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

class OperatorInfo(NodeItem):
    def __init__(self):
        super().__init__("Parameters", QIcon(":icons/actionnode.png"),
                         NodeType.OPERATORINFO)

class Operator(NodeItem):
    # class attributes
    operators = []

    # constructor
    def __init__(self, template, name=None):
        super().__init__(name, QIcon(":icons/actionnode.png"),
                         NodeType.OPERATOR)
        operator_file = template + ".yaml"
        operators_path = os.path.join(os.getcwd(), "operators")
        operator_filepath = os.path.join(operators_path, operator_file)
        logging.info(f"Operator path: {operator_filepath}")
        self.operatorInfo = OperatorInfo()

        with open(operator_filepath, "r") as f:
            operator_info = yaml.safe_load(f)
            operator_params = operator_info['parameters']
            logging.info(f"Parameters : {operator_params}")
            for item in operator_params:
                logging.info(f"{item}")

    @staticmethod
    def load_operator_list():
        Operator.operators.clear()
        operators_dir = os.path.join(os.path.join(os.curdir, "operators"), "*.yaml")
        pattern = re.compile(r"(\w*)\.yaml")
        for x in glob.glob(operators_dir):
            logging.info(x)
            match = pattern.search(x)
            if match:
                Operator.operators.append(match.group(1))
        logging.info(Operator.operators)

class Workflow(NodeItem):
    def __init__(self, name=None):
        workflowName = name if name is not None else "new_workflow"
        super().__init__(workflowName, QIcon(":/icons/workflow.png"),
                         NodeType.WORKFLOW)
        logging.info(f"{workflowName} Workflow created")

    def save(self):
        logging.info("Saving the workflow")
        workflowName = self.text()
        ret = {}
        ret['name'] = workflowName
        ret['actions'] = []
        return ret

    @staticmethod
    def load(data):
        #@todo handle key not found error
        name = data['name']
        return Workflow(name)

    def add_operator(self, template):
        logging.info(f"[Workflow] adding operator")
        self.appendRow(Operator(template, "operator"))

class Product(NodeItem):
    def __init__(self, name=None):
        super().__init__(name, QIcon(":/icons/product.png"),
                         NodeType.PRODUCT)

class ProductModel(QStandardItemModel):
    def __init__(self, name=None, parent=None):
        super().__init__(parent)
        productName = "Product1" if name == None else name
        self.root = Product(productName)
        self.appendRow(self.root)

    def add_workflow(self, workflow = None):
        w = Workflow() if workflow is None else workflow
        self.root.appendRow(w)

    def isValid(self):
        return True

    def save(self):
        product = {}
        root_index = self.index(0,0)
        productName = self.data(root_index)
        logging.info(f"Product name : {productName}")
        product['name'] = productName
        if self.hasChildren(root_index):
            logging.info("Product has workflows")
            logging.info(f"Number of workflows: {self.rowCount(root_index)}")
            workflows = []
            for row in range(self.rowCount(root_index)):
                workflow_index = self.index(row, 0, root_index)
                workflow = self.itemFromIndex(workflow_index)
                workflows.append(workflow.save())
            product['workflows'] = workflows
        else:
            logging.info("Product has NO workflows")
            product['workflows'] = []

        filename = productName + ".json"
        with open(filename, "w") as f:
            json.dump(product, f, indent=4)

    @staticmethod
    def load_from_file(filename):
        logging.info("Static method of product class")
        product = None
        with open(filename, "r") as f:
            productJson = json.load(f)
            productName = productJson['name']
            product = ProductModel(name=productName)
            workflows = productJson['workflows']
            for w in workflows:
                product.add_workflow(Workflow.load(w))
        return product

class InvalidProduct(ProductModel):
    def __init__(self):
        super().__init__()

    def isValid(self):
        return False

