from PyQt5.QtGui import QIcon
import logging

from local.node import NodeType, NodeItem
from local.operatorfactory import *
from local.operator import Operator, OperatorInfo
from local.operatorfactory import OperatorFactory

class Workflow(NodeItem):
    def __init__(self, name=None):
        workflowName = name if name is not None else "new_workflow"
        super().__init__(workflowName, QIcon(":/icons/workflow.png"),
                         NodeType.WORKFLOW)
        logging.info(f"{workflowName} Workflow created")
        self.operatorNames = []

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
        name = OperatorFactory.get_unique_name(self.operatorNames, template)
        logging.info(f"Operator name is {name}")
        self.appendRow(operator.Operator(template, name))
        self.operatorNames.append(name)
