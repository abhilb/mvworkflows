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
from local.misc import get_unique_name

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

    @property
    def state(self):
        """ Save the product state for pickling """
        return self.save()

    @state.setter
    def state(self, state):
        """ Set the state of the product from json data """
        self.load(state)

    def add_workflow(self, workflow = None):
        num_of_workflows = self.root.rowCount()
        wf_names_list = []
        for row in range(num_of_workflows):
            wf_name = self.root.child(row).text()
            wf_names_list.append(wf_name)

        if workflow is None:
            workflow_name = get_unique_name(wf_names_list, "Workflow")
            w = Workflow(workflow_name)
            self.root.appendRow(w)
        else:
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
        return product

    def clear_data(self):
        self.clear()

    def load(self, json_data):
        """Update the  model data from json"""
        self.clear()
        self.root = Product(json_data['name'])
        self.appendRow(self.root)
        workflows = json_data['workflows']
        for w in workflows:
            self.add_workflow(Workflow.load(w))

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

