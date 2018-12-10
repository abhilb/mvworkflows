from local.node import NodeItem, NodeType

class OperatorInfo(NodeItem):
    def __init__(self):
        super().__init__("Parameters", QIcon(":icons/actionnode.png"),
                         NodeType.OPERATORINFO)
        self.uuid = uuid.uuid4()

class Operator(NodeItem):
    # class attributes
    operators = []

    # constructor
    def __init__(self, template, name=None):
        super().__init__(name, QIcon(":icons/actionnode.png"),
                         NodeType.OPERATOR)
        operator_file = template + ".yaml"
        operators_path = os.path.join(os.getcwd(), "operators")
        operator_filepath = os.path.join(operators_path, operator_file)
        logging.info(f"Operator path: {operator_filepath}")
        self.operatorInfo = OperatorInfo()
        self.parameters = {}

        with open(operator_filepath, "r") as f:
            operator_info = yaml.safe_load(f)
            operator_params = operator_info['parameters']
            logging.info(f"Parameters : {operator_params}")
            self.paramters = operator_params
            for item in operator_params:
                logging.info(f"Parameter Name: {item['parameter']}")
                logging.info(f"Parameter Value: {item['value']}")
                self.operatorInfo.appendRow([QStandardItem(item['parameter']),
                    QStandardItem(item['value'])])

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

    def save(self):
        """Save the operator to file"""
        logging.info("Saving the operator")
