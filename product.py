import json
import glob
import os
import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import resources

class Workflow(QStandardItem):
    def __init__(self, name=None):
        workflowName = name if name is not None else "workflow"
        super().__init__(QIcon(":/icons/workflow.png"), workflowName)
        logging.info("Workflow created")

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

class Product(QStandardItemModel):
    def __init__(self, name=None, parent=None):
        super().__init__(parent)
        productName = "Product1" if name == None else name
        self.root = QStandardItem(QIcon(":/icons/product.png"), productName)
        self.appendRow(self.root)

    def add_workflow(self, workflow = None):
        w = Workflow() if workflow is None else workflow
        self.root.appendRow(workflow)

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
            product = Product(name=productName)
            workflows = productJson['workflows']
            for w in workflows:
                product.add_workflow(Workflow.load(w))
        return product

class InvalidProduct(Product):
    def __init__(self):
        super().__init__()

    def isValid(self):
        return False

