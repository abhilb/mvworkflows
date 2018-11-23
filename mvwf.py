
import sys
import os
import glob
import yaml

import logging
logging.basicConfig(format="%(name)s %(levelname)s %(message)s", level="INFO")

# qt imports
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QAction
from PyQt5.QtWidgets import QMenu, QTabWidget, QTableView
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# Local imports

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set window title and geometry
        self.setWindowTitle("Machine Vision Workflows")
        self.setGeometry(0, 0, 1024, 800)

        # Menu bar
        self.fileMenu = self.menuBar().addMenu("&File")
        self.newProduct = QAction("New Product", triggered=self.addProduct)
        self.fileMenu.addAction(self.newProduct)

        self.productMenu = self.menuBar().addMenu("&Product")
        self.addWorkflow = QAction("Add Workflow")
        self.productMenu.addAction(self.addWorkflow)

        self.settingsMenu = self.menuBar().addMenu("&Settings")
        self.showConfig = QAction("Show Config", triggered=self.showConfig)
        self.settingsMenu.addAction(self.showConfig)

        self.setCentralWidget(QTabWidget())

    def addProduct(self):
        logging.info("Adding a new product")
        pass
        #self.product = Product()

    def showConfig(self):
        #@todo
        configTable = QTableView()
        centralWidget = self.centralWidget()
        centralWidget.addTab(configTable, "Config")

        config = {}
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
        logging.info(config)

        configTableModel = QStandardItemModel(len(config), 2)
        for r, (k,v) in enumerate(config.items()):
            configTableModel.setItem(r,0,QStandardItem(k))
            configTableModel.setItem(r,1,QStandardItem(v))

        configTable.setModel(configTableModel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
