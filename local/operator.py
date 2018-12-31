from local.node import NodeItem, NodeType
from local import Operators
from local.parameteritem import ParameterType
from local.operatorinfo import OperatorInfo, PROVIDER_TYPE

from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QFont, QColor
from PyQt5.QtCore import Qt

import os
import yaml
import uuid
import logging

PARAMETER_TYPE_ROLE = Qt.UserRole
INPUT_TYPE_ROLE = Qt.UserRole + 1
INPUT_VALUE_OP_ID_ROLE = Qt.UserRole + 2

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
    def __init__(self, template, name, parent=None):
        super().__init__(name, QIcon(":icons/actionnode.png"),
                         NodeType.OPERATOR)
        self._uuid = uuid.uuid4()
        logging.info(Operators)
        op = Operators[template]
        self.name = name
        self.template = template
        self.workflow = parent
        self.properties = []
        self.parameters = OperatorInfo(self)

        # Operator properties
        self._number_provider = False
        self._number_list_provider = False
        self._image_provider = False
        self._string_provider = False
        self._feature_provider = False

        for item in op['parameters']:
            parameter = QStandardItem(item['parameter'])
            parameter.setIcon(QIcon(":/icons/parameter.png"))
            parameter_type = ParameterType[item['type']]
            parameter_value = item['value']
            parameter.setEditable(False)
            parameter.setSelectable(False)
            parameter.setBackground(QColor('lightblue'))

            value = QStandardItem()
            value.setData(parameter_value, Qt.DisplayRole)
            value.setData(parameter_type, Qt.UserRole)
            value.setBackground(QColor('lightblue'))

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

        if 'inputs' in op.keys():
            # inputs is a sequence of dicts
            for item in op['inputs']:
                # Each input has a name, type
                input_name = item['input_name']
                input_type = PROVIDER_TYPE[item['type']]

                value = QStandardItem()
                value.setData(ParameterType.INPUT_PARAM, Qt.UserRole)
                value.setData(input_type, Qt.UserRole + 1)
                value.setData("", Qt.UserRole + 2)
                value.setBackground(QColor(211, 211, 211))

                parameter = QStandardItem(input_name)
                parameter.setIcon(QIcon(":/icons/input.png"))
                parameter.setEditable(False)
                parameter.setSelectable(False)
                parameter.setBackground(QColor(211, 211, 211))

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

        if 'properties' in op.keys():
            for prop in op['properties']:
                try:
                    prop_enum = PROVIDER_TYPE[prop]
                    self.properties.append(prop_enum)
                except:
                    logging.error(f"Failed to set properties.... ")
                    logging.error(f"Failed to conver the property {prop} to provider enum type")
                    pass

    def get_properties(self):
        return self.properties

    def set_properties(self, props):
        """Set the properties of the operator"""
        self.properties.clear()
        self.properties.extend(props)

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
                if parameter_type is ParameterType.BOOL_PARAM:
                    parameter_item.setCheckable(True)
                    value = bool(value)
                elif parameter_type is ParameterType.INT_PARAM:
                    value = int(value)
                elif parameter_type is ParameterType.DOUBLE_PARAM:
                    value = float(value)
                elif parameter_type is ParameterType.INPUT_PARAM:
                    other_operator = self.workflow.get_operator_by_id(value)
                    if other_operator is not None:
                        value = other_operator.name
                parameter_item.setData(value, Qt.DisplayRole)


    @property
    def number_provider(self):
        """ Operator provides a number as output """
        return PROVIDER_TYPE.NUMBER in self.properties

    @property
    def number_list_provider(self):
        """ Operator provides a list of numbers as output """
        return PROVIDER_TYPE.NUMBER_LIST in self.properties

    @property
    def feature_provider(self):
        """ Operator provides a feature as output """
        return PROVIDER_TYPE.FEATURE in self.properties

    @property
    def image_provider(self):
        """ Operator provides an image as output """
        return PROVIDER_TYPE.IMAGE in self.properties

    @property
    def string_provider(self):
        """ Operator provides a string as output """
        return PROVIDER_TYPE.STRING in self.properties

    @property
    def id(self):
        return str(self._uuid)

    @id.setter
    def id(self, uuid_):
        self._uuid = uuid.UUID(uuid_)

    def provides(self, input_type):
        return input_type in self.properties

    @staticmethod
    def from_json(data, workflow = None):
        """
        Loads Operator from Json data
        """
        try:
            operator_parameter = {}
            for key in data.keys():
                if key in ['operator', 'name', 'id', 'properties']:
                    continue
                operator_parameter[key] = data[key]
            operator_type = data['operator']
            operator_name = data['name']
            operator_props = []
            logging.info("---------------------")
            logging.info("Parsing properties")
            for prop in data['properties']:
                try:
                    enum_name, prop_name = prop.split('.')
                    prop_enum = PROVIDER_TYPE[prop_name]
                    operator_props.append(prop_enum)
                except:
                    logging.error(f"Unknown provider type - {prop}")
            logging.info("---------------------")

            if 'id' in data.keys():
                operator_id = data['id']
            else:
                operator_id = str(uuid.uuid4())

        except KeyError as e:
            logging.error("Failed to load operator from json - key error")
        else:
            operator = Operator(operator_type, operator_name, workflow)
            operator.id = operator_id
            for parameter, value in operator_parameter.items():
                operator.set_parameter(parameter, value)
            logging.info(f"Operator properties: {operator_props}")
            operator.set_properties(operator_props)
            return operator

    def to_json(self):
        """Save the operator to file"""
        logging.info("Saving the operator")
        ret = {}
        ret['operator'] = self.template
        ret['name'] = self.name
        ret['id'] = self.id
        ret['properties'] = [str(x) for x in self.get_properties()]
        for row in range(self.parameters.rowCount()):
            parameter_index = self.parameters.index(row, 0)
            value_index = self.parameters.index(row, 1)
            parameter = self.parameters.itemFromIndex(parameter_index)
            value = self.parameters.itemFromIndex(value_index)
            parameter_type = value.data(Qt.UserRole)
            if parameter_type == ParameterType.INPUT_PARAM:
                ret[parameter.text()] = value.data(Qt.UserRole + 2)
            else:
                ret[parameter.text()] = value.text()
        logging.info(f"Operator: {ret}")
        return ret
