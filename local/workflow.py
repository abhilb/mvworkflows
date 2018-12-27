from PyQt5.QtGui import QIcon
import logging

from local.node import NodeType, NodeItem
from local.operatorfactory import *
from local.operator import Operator
from local.misc import get_unique_name

class Workflow(NodeItem):
    def __init__(self, workflowName):
        super().__init__(workflowName, QIcon(":/icons/workflow.png"),
                         NodeType.WORKFLOW)
        logging.info(f"{workflowName} Workflow created")
        self.operatorNames = []
        self.image_providers = []
        self.feature_providers = []
        self.number_providers = []
        self.number_list_providers = []
        self.string_providers = []

    def _add_operator(self, operator):
        if operator is None:
            return

        self.appendRow(operator)
        if operator.is_image_provider():
            self.image_providers.append(operator.uuid)
        if operator.is_feature_provider():
            self.feature_providers.append(operator.uuid)
        if operator.is_number_provider():
            self.number_provders.append(operator.uuid)
        if operator.is_number_list_provider():
            self.number_list_provders.append(operator.uuid)
        if operator.is_string_provider():
            self.string_providers.append(operator.uuid)

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
            wf._add_operator(operator)
            wf.operatorNames.append(operator.name)
        return wf

    def add_operator(self, template):
        logging.info(f"[Workflow] adding operator")
        name = get_unique_name(self.operatorNames, template)
        logging.info(f"Operator name is {name}")
        self._add_operator(Operator(template, name))
        self.operatorNames.append(name)
