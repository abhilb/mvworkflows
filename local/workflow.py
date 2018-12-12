from PyQt5.QtGui import QIcon
import logging

from local.node import NodeType, NodeItem
from local.operatorfactory import *
from local.operator import Operator
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
        operators = []
        if self.hasChildren():
            rowCount = self.rowCount()
            for i in range(rowCount):
                op = self.child(i)
                operators.append(op.to_json())
        ret['operators'] = operators
        return ret

    @staticmethod
    def load(data):
        #@todo handle key not found error
        name = data['name']
        wf = Workflow(name)
        operators = data['operators']
        for op in operators:
            operator = Operator.from_json(op)
            wf.appendRow(operator)
            wf.operatorNames.append(operator.name)
        return wf

    def add_operator(self, template):
        logging.info(f"[Workflow] adding operator")
        name = OperatorFactory.get_unique_name(self.operatorNames, template)
        logging.info(f"Operator name is {name}")
        self.appendRow(Operator(template, name))
        self.operatorNames.append(name)
