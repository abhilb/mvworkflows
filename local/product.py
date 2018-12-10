import json
import glob
import os
import re
import yaml
import uuid
import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from local import resources
from local.node import NodeItem, NodeType
from local.workflow import Workflow
from local.operator import Operator

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

