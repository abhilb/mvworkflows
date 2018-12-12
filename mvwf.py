import sys
import os
import glob
import yaml
import re
import json
import pickle
import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

# qt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle

# Local imports
from local.product import *
from local import Operators

# globals
config = {}
recent_files_list = []
app = QApplication(sys.argv)

def app_init():
    """
    Application initialization
    It carries out the following functions
    a) Load the config
    b) Load the recently opened products list
    """

    # Load the config
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

    # Load the recently opened products list
    global recent_files_list

    if os.path.exists("recentfiles.dat"):
        with open("recentfiles.dat", "rb") as f:
            recent_files_list = pickle.load(f)
    print(recent_files_list)

class MainWindow(QMainWindow):
    MAX_RECENT_FILES_COUNT = 5
    """
    Workflow Editor widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        app_init()
        print(recent_files_list)

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
        self.fileMenu.addSeparator()
        self.recentFilesMenu = self.fileMenu.addMenu("Recent Products")
        self.recentFileActions = []
        for item in recent_files_list:
            logging.info(f"Adding this to the recent file actions : {item}")
            self.recentFileActions.append(QAction(item, triggered=self.openRecentFile))

        for action in self.recentFileActions:
            self.recentFilesMenu.addAction(action)

        self.productMenu = self.menuBar().addMenu("&Product")
        self.newWorkflow = QAction("Add Workflow", triggered=self.addWorkflow)
        self.productMenu.addAction(self.newWorkflow)

        self.operatorMenu = self.menuBar().addMenu("&Operator")
        self.addOperatorAction = QAction("Add Operator", triggered=self.addOperator)
        self.operatorMenu.addAction(self.addOperatorAction)

        self.settingsMenu = self.menuBar().addMenu("&Settings")
        self.showConfig = QAction("Show Config", triggered=self.showConfig)
        self.showProductExplorer = QAction("Show Product Explorer", triggered=self.show_product_explorer)
        self.showOperatorEditor = QAction("Show Operator Editor", triggered=self.show_operator_editor)
        self.settingsMenu.addAction(self.showConfig)
        self.settingsMenu.addAction(self.showProductExplorer)
        self.settingsMenu.addAction(self.showOperatorEditor)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.aboutQtAction = QAction("About Qt", triggered=QApplication.aboutQt)
        self.aboutAction = QAction("About", triggered=self.show_about_dlg)
        self.helpMenu.addAction(self.aboutQtAction)
        self.helpMenu.addAction(self.aboutAction)

        # Tool bar

        # Status bar
        statusBarWidget = QWidget()
        statusBarWidget.setLayout(QHBoxLayout())
        statusBarWidget.layout().addWidget(QLabel("Machine Vision Workflows"))
        self.statusBar().addPermanentWidget(statusBarWidget)

        self.setCentralWidget(QTabWidget())
        centralWidget = self.centralWidget()
        centralWidget.setTabsClosable(True)
        centralWidget.tabCloseRequested.connect(self.onTabClose)

        # Product Explorer
        self.productExplorer = QTreeView()
        self.productExplorer.setHeaderHidden(True)
        self.productExplorer.clicked.connect(self.product_item_selected)
        self.dockingWidget = QDockWidget("Product explorer", self)
        self.dockingWidget.setWidget(self.productExplorer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockingWidget)

        # Operator Editor
        self.operatorEditor = QTreeView()
        self.operatorEditor.setHeaderHidden(True)
        self.operatorEditorDock = QDockWidget("Operator editor", self)
        self.operatorEditorDock.setWidget(self.operatorEditor)
        self.addDockWidget(Qt.RightDockWidgetArea, self.operatorEditorDock)

        self.configIsOpen = False
        self.configTabIndex = -1
        self.product = InvalidProduct()

    def product_item_selected(self, index):
        model = index.model()
        item = model.itemFromIndex(index)
        if item.node_type == NodeType.OPERATOR:
            self.operatorEditor.setModel(item.parameters)

    def openRecentFile(self):
        action = self.sender()
        if action:
            filename = action.text()
            logging.info(f"Open the product: {filename}")
            self.product = ProductModel.load_from_file(filename)
            self.productExplorer.setModel(self.product)
            self.productExplorer.expandAll()

    def show_about_dlg(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("About")
        msgBox.setText("Machine Vision Workflows")
        msgBox.setInformativeText("v.0.0.1")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def show_product_explorer(self):
        logging.info("Show product explorer")
        if self.dockingWidget:
            self.dockingWidget.setVisible(True)

    def show_operator_editor(self):
        logging.info("Show operator editor")
        if self.operatorEditorDock:
            self.operatorEditorDock.setVisible(True)

    def closeEvent(self, event):
        logging.info("Application close event")
        with open("recentfiles.dat", "wb") as f:
            pickle.dump(recent_files_list, f)
        QCloseEvent(event)

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
        self.product = ProductModel()
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
            self.product = ProductModel.load_from_file(fileName)
            self.productExplorer.setModel(self.product)
            recent_files_list.append(fileName)

    def addWorkflow(self):
        if self.product.isValid():
            logging.info("Adding a new workflow")
            self.product.add_workflow()
        else:
            pass

    def addOperator(self):
        if self.product.isValid():
            selectionModel = self.productExplorer.selectionModel()
            currentIndex = selectionModel.currentIndex()
            node = self.product.itemFromIndex(currentIndex)
            if node is not None:
                nodeType = node.node_type
                if nodeType == NodeType.WORKFLOW:
                    logging.info("Node is of type workflow")
                    operator, ok = QInputDialog.getItem(self, "Operator",
                                                        "Operator: ",
                                                        Operators.keys(),
                                                        0, False)
                    node.add_operator(operator)

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
