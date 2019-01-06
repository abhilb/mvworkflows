"""
Operator Info - Model for Operator Info
"""
import logging
from enum import Enum
from PyQt5.QtGui import QStandardItemModel

logging.basicConfig(format="%(levelname)s - %(message)s", level="INFO")

# Provider types
PROVIDER_TYPE = Enum('PROVIDER_TYPE', 'IMAGE, NUMBER, NUMBER_LIST, FEATURE, STRING')


class OperatorInfo(QStandardItemModel):
    """Class to hold operator info - parameters, inputs and properties"""
    def __init__(self, operator, parent=None):
        super().__init__(parent)
        self._operator = operator
        self._workflow = operator.workflow

    def get_providers(self, input_type):
        num_of_operators = self._workflow.rowCount()
        prior_operators = []
        for row in range(num_of_operators):
            op = self._workflow.child(row)
            print(f"Operator: {op.id} Image provider {op.image_provider}")
            if op.id != self._operator.id and op.provides(input_type):
                prior_operators.append(op)

        print(f"Prior operartors {prior_operators}")
        return prior_operators

    def get_outputs(self, input_type):
        num_of_operators = self._workflow.rowCount()
        prior_operators = []
        for row in range(num_of_operators):
            op = self._workflow.child(row)
            if op.id != self._operator.id:
                keys = [PROVIDER_TYPE[x] for x in op.outputs.keys()]
                if PROVIDER_TYPE.IMAGE in keys:
                    image_outputs = op.outputs['IMAGE']
                    for output in image_outputs:
                        prior_operators.append(output)

        print(f"Prior operartors {prior_operators}")
        return prior_operators

