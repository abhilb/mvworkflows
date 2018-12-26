from local.node import NodeItem, NodeType
from local import Operators
from local.parameteritem import ParameterItem, ParameterType
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QFont
from PyQt5.QtCore import Qt

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
        self._uuid = uuid.uuid4()
        op = Operators[template]
        self.parameters = QStandardItemModel()
        self.name = name
        self.template = template

        # Operator properties
        self._number_provider = False
        self._number_list_provider = False
        self._image_provider = False
        self._string_provider = False
        self._feature_provider = False

        for item in op['parameters']:
            parameter = QStandardItem(item['parameter'])
            parameter_type = ParameterType[item['type']]
            parameter_value = item['value']
            value = QStandardItem()
            value.setData(parameter_value, Qt.DisplayRole)
            value.setData(parameter_type, Qt.UserRole)
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

            self.parameters.appendRow([parameter, value])

    def set_parameter(self, name, value):
        """
        Update the value of the parameter
        Raise exception if parameter not found
        """
        row_count = self.parameters.rowCount()
        for row in range(row_count):
            parameter_name = self.parameters.item(row, 0).text()
            parameter_item = self.parameters.item(row, 1)
            if parameter_name == name:
                parameter_type = parameter_item.data(Qt.UserRole)
                print(f"{parameter_name} {parameter_type}")
                if parameter_type is ParameterType.BOOL_PARAM:
                    parameter_item.setCheckable(True)
                    value = bool(value)
                elif parameter_type is ParameterType.INT_PARAM:
                    value = int(value)
                elif parameter_type is ParameterType.DOUBLE_PARAM:
                    value = float(value)

                parameter_item.setData(value, Qt.DisplayRole)

    def is_number_provider(self):
        """ Operator provides a number as output """
        return self._number_provider

    def is_number_list_provider(self):
        """ Operator provides a list of numbers as output """
        return self._number_list_provider

    def is_2d_feature_provider(self):
        """ Operator provides a feature as output """
        return self._feature_provider

    def is_image_provider(self):
        """ Operator provides an image as output """
        return self._image_provider

    def is_feature_provider(self):
        """ Operator provides a feature as output """
        return self._feature_provider

    def is_string_provider(self):
        """ Operator provides a string as output """
        return self._string_provider

    @property
    def id(self):
        return str(self._uuid)

    @id.setter
    def id(self, uuid_):
        self._uuid = uuid.UUID(uuid_)

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
            operator_id = data['id']

            # Check if number provider
            if 'number_provider' in data.keys():
                self.is_number_provider = data['number_provider']

            # Check if number list provider
            if 'number_list_provider' in data.keys():
                self.is_number_list_provider = data['number_list_provider']

            # Check if image provider
            if 'image_provider' in data.keys():
                self.is_image_provider = data['image_provider']

        except KeyError as e:
            logging.error("Failed to load operator from json - key error")
        else:
            operator = Operator(operator_type, operator_name)
            operator.id = operator_id
            for parameter, value in operator_parameter.items():
                operator.set_parameter(parameter, value)
            return operator

    def to_json(self):
        """Save the operator to file"""
        logging.info("Saving the operator")
        ret = {}
        ret['operator'] = self.template
        ret['name'] = self.name
        ret['id'] = self.id
        for row in range(self.parameters.rowCount()):
            parameter_index = self.parameters.index(row, 0)
            value_index = self.parameters.index(row, 1)
            parameter = self.parameters.itemFromIndex(parameter_index)
            value = self.parameters.itemFromIndex(value_index)
            print(f"{row+1} : {parameter.text()} : {value.text()}")
            ret[parameter.text()] = value.text()
        return ret
