
import sys
import os
import glob
import yaml
import re
import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

# qt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle

app = QApplication(sys.argv)

# Local imports
from product import *

operators_dir = os.path.join(os.path.join(os.curdir, "operators"), "*.yaml")
operators = []
pattern = re.compile(r"(\w*)\.yaml")
for x in glob.glob(operators_dir):
    logging.info(x)
    match = pattern.search(x)
    if match:
        operators.append(match.group(1))
logging.info(operators)

config = {}
with open("config.yaml") as f:
    config = yaml.safe_load(f)
logging.info(config)
products_dir = config['products_path']
product_files = glob.glob(os.path.join(products_dir, "*.json"))
pattern = re.compile(r"(\w*)\.json")
products = []
for x in product_files:
    match = pattern.search(x)
    if match:
        products.append(match.group(1))
logging.info(products)

class MainWindow(QMainWindow):
    """
    Workflow Editor widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set window title and geometry
        self.setWindowTitle("Machine Vision Workflows")
        self.setGeometry(0, 0, 1024, 800)

        # Menu bar
        self.fileMenu = self.menuBar().addMenu("&File")
        self.newProduct = QAction("New Product", triggered=self.addProduct)
        self.openProduct = QAction("Open Product", triggered=self.openProduct)
        self.saveProduct = QAction("Save Product", triggered=self.saveProduct)
        self.fileMenu.addAction(self.newProduct)
        self.fileMenu.addAction(self.openProduct)
        self.fileMenu.addAction(self.saveProduct)

        self.productMenu = self.menuBar().addMenu("&Product")
        self.newWorkflow = QAction("Add Workflow", triggered=self.addWorkflow)
        self.productMenu.addAction(self.newWorkflow)

        self.operatorMenu = self.menuBar().addMenu("&Operator")
        self.addOperatorAction = QAction("Add Operator", triggered=self.addOperator)
        self.operatorMenu.addAction(self.addOperatorAction)

        self.settingsMenu = self.menuBar().addMenu("&Settings")
        self.showConfig = QAction("Show Config", triggered=self.showConfig)
        self.settingsMenu.addAction(self.showConfig)

        self.setCentralWidget(QTabWidget())
        centralWidget = self.centralWidget()
        centralWidget.setTabsClosable(True)
        centralWidget.tabCloseRequested.connect(self.onTabClose)

        # Product Explorer
        self.productExplorer = QTreeView()
        self.productExplorer.setHeaderHidden(True)
        self.dockingWidget = QDockWidget("Product explorer", self)
        self.dockingWidget.setWidget(self.productExplorer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockingWidget)

        self.configIsOpen = False
        self.configTabIndex = -1

        self.product = InvalidProduct()

    def onTabClose(self, index):
        if index == self.configTabIndex:
            self.configIsOpen = False
            self.configTabIndex = -1
        self.centralWidget().removeTab(index)

    def addProduct(self):
        logging.info("Adding a new product")
        if self.dockingWidget.isVisible():
            pass
        else:
            self.dockingWidget.show()
        pass
        self.product = Product()
        self.productExplorer.setModel(self.product)

    def saveProduct(self):
        if self.product.isValid():
            self.product.save()
        else:
            pass

    def openProduct(self):
        fileName, _ = QFileDialog.getOpenFileName(self)
        if fileName:
            logging.info(f"Opening {fileName}")
            self.product = Product.load_from_file(fileName)
            self.productExplorer.setModel(self.product)

    def addWorkflow(self):
        if self.product.isValid():
            logging.info("Adding a new workflow")
            self.product.add_workflow()
        else:
            pass

    def addOperator(self):
        if self.product.isValid():
            operator, ok = QInputDialog.getItem(self, "Operator", "Operator: ", operators, 0, False)
            logging.info(f"Selected {operator}")
            selectionModel = self.productExplorer.selectionModel()
            currentIndex = selectionModel.currentIndex()
            logging.info(f"Current index row:{currentIndex.row()} column: {currentIndex.column()}")

    def showConfig(self):
        if not self.configIsOpen:
            configTable = QTableView()
            centralWidget = self.centralWidget()
            self.configTabIndex = centralWidget.addTab(configTable, "Config")

            config = {}
            with open("config.yaml") as f:
                config = yaml.safe_load(f)
            logging.info(config)

            configTableModel = QStandardItemModel(len(config), 2)
            for r, (k,v) in enumerate(config.items()):
                configTableModel.setItem(r,0,QStandardItem(k))
                configTableModel.setItem(r,1,QStandardItem(v))

            configTable.setModel(configTableModel)
            self.configIsOpen = True

if __name__ == "__main__":
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
