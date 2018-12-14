from local.node import NodeItem, NodeType
from local import Operators
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QFont

import os
import yaml
import uuid
import logging

class Operator(NodeItem):
    """
    Represents a machine vision operation
    Parameters and the description of each operation is specified
    in a yaml file. This class instantiates an operation.
    Serialization of the instance will save the name, type and
    parameters of the operation. Deserialization will then restore
    the parameter values.
    """
    # class attributes
    operators = []

    # constructor
    def __init__(self, template, name=None):
        super().__init__(name, QIcon(":icons/actionnode.png"),
                         NodeType.OPERATOR)
        op = Operators[template]
        self.parameters = QStandardItemModel()
        self.name = name
        self.template = template
        for item in op['parameters']:
            parameter = QStandardItem(item['parameter'])
            value = QStandardItem(str(item['value']))
            parameter.setEditable(False)
            parameter.setSelectable(False)

            parameter_font = parameter.font()
            parameter_font.setWeight(QFont.Bold)
            parameter_font_size = parameter_font.pointSize()
            if parameter_font_size == -1:
                parameter_font.setPixelSize(parameter_font.pixelSize() + 1)
            else:
                parameter_font.setPointSize(parameter_font_size + 1)
            parameter_font.setItalic(True)
            parameter_font.setCapitalization(QFont.AllUppercase)

            parameter.setFont(parameter_font)
            value.setEditable(True)
            # value.setData(item['value'], Qt.EditRole)
            self.parameters.appendRow([parameter, value])

    def set_parameter(self, name, value):
        """
        Update the value of the parameter
        Raise exception if parameter not found
        """
        row_count = self.rowCount()
        for row in range(row_count):
            parameter = self.child(row, 0)
            parameter_name = parameter.text()
            parameter_value = self.child(row, 1)
            if parameter_name == name:
               parameter_value.setText(value)

    def has_result(self):
        """
        Returns True or False based on if there is
        result available for this operator. When the Operator
        Model is changed then the Result has to be reset.
        This API can be used by the viewer to display the
        result of the operator.
        """
        pass

    def is_number_provider(self):
        pass

    def is_number_list_provider(self):
        pass

    def is_2d_feature_provider(self):
        pass

    def is_image_provider(self):
        """
        Returns True if this operator is an image provider
        Operator.
        """
        pass

    @staticmethod
    def from_json(data):
        """
        Loads Operator from Json data
        """
        try:
            operator_parameter = {}
            for key in data.keys():
                if key == 'operator' or key == 'name':
                    continue
                operator_parameter[key] = data[key]
            operator_type = data['operator']
            operator_name = data['name']
        except KeyError as e:
            logging.error("Failed to load operator from json - key error")
        else:
            operator = Operator(operator_type, operator_name)
            for parameter, value in operator_parameter.items():
                print(f"{parameter} : {value}")
                operator.set_parameter(parameter, value)
            return operator

    def to_json(self):
        """Save the operator to file"""
        logging.info("Saving the operator")
        ret = {}
        ret['operator'] = self.template
        ret['name'] = self.name
        for row in range(self.parameters.rowCount()):
            parameter_index = self.parameters.index(row, 0)
            value_index = self.parameters.index(row, 1)
            parameter = self.parameters.itemFromIndex(parameter_index)
            value = self.parameters.itemFromIndex(value_index)
            print(f"{row+1} : {parameter.text()} : {value.text()}")
            ret[parameter.text()] = value.text()
        return ret
