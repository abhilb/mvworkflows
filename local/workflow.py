"""
Module: Workflow
Describes the Workflow component
"""
import logging

from PyQt5.QtGui import QIcon
from enum import Enum
from local.node import NodeType, NodeItem
from local.operatorfactory import *
from local.operator import Operator
from local.misc import get_unique_name
from local.operatorinfo import PROVIDER_TYPE

class Workflow(NodeItem):
    def __init__(self, workflowName):
        super().__init__(workflowName, QIcon(":/icons/workflow.png"),
                         NodeType.WORKFLOW)
        self.logger = logging.getLogger(f"[{self.__class__.__name__}]")
        self.logger.info(f"{workflowName} Workflow created")
        self.providers = {}
        self.operatorNames = []
        for provider_type in PROVIDER_TYPE:
            self.providers[provider_type] = []

    def _add_operator(self, operator):
        if operator is None:
            self.logger.warning(f"Operator is NONE")
            return

        self.appendRow(operator)
        if operator.image_provider:
            self.providers[PROVIDER_TYPE.IMAGE].append(operator)
        if operator.feature_provider:
            self.providers[PROVIDER_TYPE.FEATURE].append(operator)
        if operator.number_provider:
            self.providers[PROVIDER_TYPE.NUMBER].append(operator)
        if operator.number_list_provider:
            self.providers[PROVIDER_TYPE.NUMBER_LIST].append(operator)
        if operator.string_provider:
            self.providers[PROVIDER_TYPE.STRING].append(operator)

    def get_operator_by_id(self, operator_id):
        if self.hasChildren():
            rowCount = self.rowCount()
            for row in range(rowCount):
                operator = self.child(row)
                if operator.id == operator_id:
                    return operator
        return None

    def save(self):
        self.logger.info("Saving the workflow")
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
            operator = Operator.from_json(op, wf)
            wf._add_operator(operator)
            wf.operatorNames.append(operator.name)
        return wf

    def add_operator(self, template):
        self.logger.info(f"[Workflow] adding operator")
        name = get_unique_name(self.operatorNames, template)
        self.logger.info(f"Operator name is {name}")
        self._add_operator(Operator(template, name, self))
        self.operatorNames.append(name)
