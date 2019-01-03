"""
Model for Product Explorer Widget
"""
import uuid
from PyQt5.QtGui import QStandardItemModel

def singleton(cls):
    instances = {}
    def get_instance(cls):
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance

class Operator():
    def __init__(self, name, template):
        self._id = uuid.uuid4()
        self._name = name
        self._parameters = {}
        self._inputs = {}

    def __str__(self):
        op_str = f"""
            name = {self._name}
        """

    @property
    def id(self):
        return self._id

class Workflow():
    def __init__(self, name):
        self._id = uuid.uuid4()
        self._name = name
        self._operators = []

    def __str__(self):
        wf_str = f"""
            name: {self._name}
            id = {self._id}
        """
        for op in self._operators:
            wf_str.append(op)
        return wf_str

    @property
    def id(self):
        return self._id

@singleton
class Product():
    __workflows = []
    __metadata = {}

    def __str__(self):
        product_str = f"""
        name = {self.__metadata['name']}
        """
        for wf in __workflows:
            product_str.append(str(wf))
        return product_str

    @property
    def name(self):
        return self._name

    def add_workflow(self, wf):
        self.__workflows.append(wf)

    def del_workflow(self, wf_id):
        for wf in self.__workflows:
            if wf.id == wf_id:
                self.__workflows.remove(wf)
                break
        else:
            logger.warning(f"Workflow with id : {wf_id} is not found in product")

class ProductExplorerModel(QStandardItemModel):
    """
    Model for Product explorer widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._product = Product()

    def add_workflow(self, wf_name):
        self._product.add_workflow(Workflow(wf_name))
