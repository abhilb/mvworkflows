import sys
import os
import glob
import yaml
import re
import json
import pickle
import sqlite3
import uuid

from collections import deque
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String
from sqlalchemy.sql import select, and_

import logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level="INFO")
logger = logging.getLogger("[mvwf]")

# qt imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#import qdarkstyle

# Local imports
from local import Operators
from local.product import *
from local.node import NodeType
from local.paramdelegate import ParamDelegate
from local.taskselector import TaskSelector
from local.create_task import CreateTask
from local.product_explorer import ProductExplorer
from local.client_worker import ClientWorker
from changemanager import ChangeManager

# globals
config = {}
recent_files_list = []
app = QApplication(sys.argv)
db = create_engine("sqlite:///mvwf.db")

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
    logger.info(config)
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

class MainWindow(QMainWindow):
    MAX_RECENT_FILES_COUNT = 5
    """
    Workflow Editor widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        app_init()

        # Set window title and geometry
        self.setWindowTitle("Machine Vision Workflows")
        self.setGeometry(0, 0, 1024, 800)

        ##############
        # Actions
        ##############
        self.newProduct = QAction(QIcon(":icons/new.png"), "New Product", triggered=self.addProduct)
        self.openProduct = QAction(QIcon(":icons/open.png"), "Open Product", triggered=self.openProduct)
        self.saveProduct = QAction(QIcon(":icons/save.png"), "Save Product", triggered=self.saveProduct)
        self.newWorkflow = QAction(QIcon(":/icons/workflow.png"),"Add Workflow", triggered=self.addWorkflow)
        self.addOperatorAction = QAction(QIcon(":/icons/actionnode.png"),"Add Operator", triggered=self.addOperator)
        self.showConfig = QAction("Show Config", triggered=self.showConfig)
        self.showProductExplorer = QAction("Show Product Explorer", triggered=self.show_product_explorer)
        self.showOperatorEditor = QAction("Show Operator Editor", triggered=self.show_operator_editor)
        self.aboutQtAction = QAction("About Qt", triggered=QApplication.aboutQt)
        self.aboutAction = QAction("About", triggered=self.show_about_dlg)
        self.recentFileActions = []
        for item in recent_files_list:
            self.recentFileActions.append(QAction(QIcon(":icons/product.png"),
                item, triggered=self.openRecentFile))

        self.undo_change_action = QAction(QIcon(":icons/undo.png"), "Undo change", triggered=self.undo_change)
        self.undo_change_action.setEnabled(False)
        self.redo_change_action = QAction(QIcon(":icons/redo.png"), "Redo change", triggered=self.redo_change)
        self.redo_change_action.setEnabled(False)
        self.execute_action = QAction(QIcon(":icons/execute.png"), "Execute", triggered=self.execute)
        self.create_task_action = QAction("Create new task", triggered=self.create_task)
        self.execute_action.setEnabled(False)

        # Action short cuts
        self.newProduct.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        self.openProduct.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        self.saveProduct.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))

        ###############
        # Menu bar
        ###############
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newProduct)
        self.fileMenu.addAction(self.openProduct)
        self.fileMenu.addAction(self.saveProduct)
        self.fileMenu.addSeparator()
        self.recentFilesMenu = self.fileMenu.addMenu("Recent Products")

        for action in self.recentFileActions:
            self.recentFilesMenu.addAction(action)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.newWorkflow)
        self.editMenu.addAction(self.addOperatorAction)
        self.editMenu.addAction(self.create_task_action)

        self.settingsMenu = self.menuBar().addMenu("&Settings")
        self.settingsMenu.addAction(self.showConfig)
        self.settingsMenu.addAction(self.showProductExplorer)
        self.settingsMenu.addAction(self.showOperatorEditor)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutQtAction)
        self.helpMenu.addAction(self.aboutAction)

        ###############
        # Tool bar
        ###############
        self.file_toolbar = QToolBar(self)
        self.file_toolbar.setFloatable(False)
        self.file_toolbar.setMovable(False)
        self.file_toolbar.addAction(self.newProduct)
        self.file_toolbar.addAction(self.openProduct)
        self.file_toolbar.addAction(self.saveProduct)
        self.file_toolbar.addSeparator()
        self.file_toolbar.addAction(self.undo_change_action)
        self.file_toolbar.addAction(self.redo_change_action)
        self.file_toolbar.addSeparator()
        self.file_toolbar.addAction(self.execute_action)
        self.file_toolbar.addSeparator()
        self.addToolBar(self.file_toolbar)

        ###############
        # Status bar
        ###############
        statusBarWidget = QWidget()
        statusBarWidget.setLayout(QHBoxLayout())
        statusBarWidget.layout().addWidget(QLabel("<b>Machine Vision Workflows</b>"))
        statusBarWidget.layout().addWidget(QLabel("Created by <em>Abhilash Babu J</em>"))
        self.statusBar().addPermanentWidget(statusBarWidget)


        ################
        # Central Widget
        ################
        self.setCentralWidget(QTabWidget())
        centralWidget = self.centralWidget()
        centralWidget.setTabsClosable(True)
        # centralWidget.setStyleSheet("""
        #         QWidget {
        #         background-color: rgb(40, 40, 40);
        #         }
        #         """)
        centralWidget.tabCloseRequested.connect(self.onTabClose)

        ###################
        # Product Explorer
        ###################
        self.productExplorer = ProductExplorer()
        self.productExplorer.setHeaderHidden(True)
        self.productExplorer.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.productExplorer.clicked.connect(self.product_item_selected)
        self.productExplorer.operator_selected.connect(self.operator_selected)
        self.productExplorer.product_selected.connect(self.product_selected)
        self.productExplorer.workflow_selected.connect(self.workflow_selected)
        self.productExplorer.model_is_set.connect(self.enable_execute_action)

        self.dockingWidget = QDockWidget("Product explorer", self)
        self.dockingWidget.setWidget(self.productExplorer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockingWidget)

        # Operator Editor
        self.operatorEditor = QTreeView()
        self.operatorEditor.setItemDelegate(ParamDelegate())
        self.operatorEditor.setHeaderHidden(True)
        self.operatorEditor.setRootIsDecorated(False)
        self.operatorEditorDock = QDockWidget("Operator editor", self)
        self.operatorEditorDock.setWidget(self.operatorEditor)
        self.addDockWidget(Qt.RightDockWidgetArea, self.operatorEditorDock)

        self.configIsOpen = False
        self.configTabIndex = -1
        self.product = InvalidProduct()

        self.change_manager = ChangeManager()
        self.change_manager.index_changed.connect(self.update_undo_redo)

    def enable_execute_action(self):
        self.execute_action.setEnabled(True)

    def product_item_selected(self, event):
        selectedIndexes = self.productExplorer.selectedIndexes()
        if len(selectedIndexes) == 0:
            return

        model = selectedIndexes[0].model()
        item = model.itemFromIndex(selectedIndexes[0])
        if item.node_type == NodeType.OPERATOR:
            operatorWidget = QTreeView()
            operatorWidget.setItemDelegate(ParamDelegate())
            operatorWidget.setModel(item.parameters)
            self.centralWidget().addTab(operatorWidget, "Operator")


    def contextMenuEvent(self, event):
        """
        @override
        Overrides the context menu event. Handles the context menu for items
        in the product explorer widget
        """
        selectedIndexes = self.productExplorer.selectedIndexes()
        if len(selectedIndexes) == 0:
            logger.info("Nothing is selected in the product explorer")
            return

        model = selectedIndexes[0].model()
        item = model.itemFromIndex(selectedIndexes[0])

        context_menu = QMenu(self)
        if item.node_type == NodeType.WORKFLOW:
            context_menu.addAction(self.addOperatorAction)
        elif item.node_type == NodeType.PRODUCT:
            context_menu.addAction(self.newWorkflow)
        else:
            logger.info("Selected item is neither a workflow nor product")
            return

        context_menu.exec_(self.mapToGlobal(event.pos()))

    def execute(self):
        self.client_worker = ClientWorker(self)
        self.client_worker.completedSignal.connect(self.completed_execution)
        self.client_worker.start()
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setWindowTitle("Workflow Execution in progress")
        self.progress_dialog.setModal(True)
        self.progress_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.hide()
        self.progress_dialog.setRange(0,0)
        self.progress_dialog.show()

    def completed_execution(self):
        """
        Slot to capture the completed signal from the client worker thread
        """
        logger.info("Client worker thread is killed")
        self.progress_dialog.hide()
        self.progress_dialog = None
        print(self.client_worker.result)

    def create_task(self):
        create_task_dlg = CreateTask(self)
        create_task_dlg.exec()

    def update_undo_redo(self):
        """ Enable/Disable the undo and redo buttons based on if undo/redo is possible """
        self.undo_change_action.setEnabled(self.change_manager.is_undo_possible())
        self.redo_change_action.setEnabled(self.change_manager.is_redo_possible())

    def workflow_selected(self, index):
        """ When a workflow is selected in the product explorer clear the opertor editor """
        self.operatorEditor.setModel(QStandardItemModel())

    def product_selected(self, index):
        """ When a product is selected in the product explorer clear the operator editor"""
        self.operatorEditor.setModel(QStandardItemModel())

    def operator_selected(self, index):
        """
        Set the model for the operator editor based on the operator selected
        based on the operator selected in the Product explorer
        """
        model = index.model()
        item = model.itemFromIndex(index)
        if item.node_type == NodeType.OPERATOR:
            self.operatorEditor.setModel(item.parameters)

    def openRecentFile(self):
        """ Slot for the open recent file action """
        action = self.sender()
        if action:
            filename = action.text()
            logger.info(f"Open the product: {filename}")
            self.product = ProductModel.load_from_file(filename)
            self.product.itemChanged.connect(self.on_product_changed)
            self.product.rowsInserted.connect(self.on_product_changed)
            self.product.rowsRemoved.connect(self.on_product_changed)
            self.product.rowsMoved.connect(self.on_product_changed)
            self.productExplorer.set_model(self.product)
            self.productExplorer.expandAll()

    def keyPressEvent(self, event):
        """ Handle key press events """
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            if self.change_manager.is_undo_possible():
                self.change_manager.ignore_changes = True
                self.product = self.change_manager.undo(self.product)
                self.change_manager.ignore_changes = False
        elif event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier:
            if self.change_manager.is_redo_possible():
                self.change_manager.ignore_changes = True
                self.product = self.change_manager.redo(self.product)
                self.change_manager.ignore_changes = False

    def undo_change(self):
        self.change_manager.ignore_changes = True
        self.product = self.change_manager.undo(self.product)
        self.change_manager.ignore_changes = False
        self.productExplorer.expandAll()

    def redo_change(self):
        self.change_manager.ignore_changes = True
        self.product = self.change_manager.redo(self.product)
        self.change_manager.ignore_changes = False
        self.productExplorer.expandAll()

    def on_product_changed(self, item):
        """ Slot to track product changes """
        logger.info("Product changed")
        self.change_manager.save_state(self.product)

    def show_about_dlg(self):
        """ Show the about dialog """
        msgBox = QMessageBox(self)
        msgBox.setIconPixmap(QIcon(":/icons/logo.png").pixmap(QSize(64,64)))
        msgBox.setWindowTitle("About")
        msgBox.setText("""
        <h1>Machine Vision Workflows</h1>
        <br/>
        <h3>Version : v.0.0.1</h3>
        """)
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setInformativeText("""
        icon source: www.flaticon.com, www.iconfinder.com
        """)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def show_product_explorer(self):
        """ Show the product exeplorer """
        logger.info("Show product explorer")
        if self.dockingWidget:
            self.dockingWidget.setVisible(True)

    def show_operator_editor(self):
        """ Show the operator editor """
        logger.info("Show operator editor")
        if self.operatorEditorDock:
            self.operatorEditorDock.setVisible(True)

    def closeEvent(self, event):
        """ Slot for the application close event """
        logger.info("Application close event")

        # Add the currently open product to recent files list
        with open("recentfiles.dat", "wb") as f:
            pickle.dump(recent_files_list, f)

        # Continue with the close event
        QCloseEvent(event)

    def onTabClose(self, index):
        """ Slot for tab close event """
        if index == self.configTabIndex:
            self.configIsOpen = False
            self.configTabIndex = -1
        self.centralWidget().removeTab(index)

    def addProduct(self):
        """ Add a new product """
        if self.dockingWidget.isVisible():
            pass
        else:
            self.dockingWidget.show()
        pass
        self.product_id = str(uuid.uuid4())
        self.product = ProductModel()
        self.product.itemChanged.connect(self.on_product_changed)
        self.product.rowsInserted.connect(self.on_product_changed)
        self.product.rowsRemoved.connect(self.on_product_changed)
        self.product.rowsMoved.connect(self.on_product_changed)
        self.productExplorer.set_model(self.product)
        self.change_manager.save_state(self.product)

    def saveProduct(self):
        """ Save the currently open product """
        if self.product.isValid():
            product_json = json.dumps(self.product.save(), indent=4)
            #TODO: Check if the db already has this product.
            # in that case only update the product instead of
            # insert.
            with db.connect() as con:
                meta = MetaData(db)
                products_tbl = Table('products', meta, autoload=True)
                query = select([products_tbl])
                query_result = con.execute(query)
                products_list = query_result.fetchall()
                print(products_list)

                #TODO: Add id field to product to uniquely identify a product. 
                # Multiple products can have the same name. 
                product_names = []
                for p in products_list:
                    idx, product_ = p
                    product_dict_ = json.loads(product_)
                    product_names.append(product_dict_["name"])

                if product_json["name"] in product_names:
                    #TODO: Add update statement here
                    pass
                else:
                    ins = products_tbl.insert().values(product=product_json)
                    con.execute(ins)

            self.change_manager.clear()
        else:
            pass

    def openProduct(self):
        """ Open a product """
        #TODO:
        # Select all the products available in the database and
        # show a combo box updated with that list. User can then
        # choose the product from there.
        with db.connect() as con:
            meta = MetaData(db)
            products_tbl = Table('products', meta, autoload=True)
            query = select([products_tbl])
            query_result = con.execute(query)
            products = [x[1] for x in query_result.fetchall()]
            product_names = [json.loads(x)["name"] for x in products]
            product_name, ok = QInputDialog.getItem(self, "", "", product_names, -1, False)
            if product_name:
                self.product = ProductModel()
                self.product.load(json.loads(products[product_names.index(product_name)]))
                self.product.itemChanged.connect(self.on_product_changed)
                self.product.rowsInserted.connect(self.on_product_changed)
                self.product.rowsRemoved.connect(self.on_product_changed)
                self.product.rowsMoved.connect(self.on_product_changed)
                self.productExplorer.set_model(self.product)

        #TODO: Recent files
        #     if fileName in recent_files_list:
        #         recent_files_list.remove(fileName)
        #     recent_files_list.append(fileName)

    def addWorkflow(self):
        """ Add a workflow to the currently open product """
        if self.product.isValid():
            logger.info("Adding a new workflow")
            self.product.add_workflow()
            self.productExplorer.expandAll()
        else:
            pass

    def addOperator(self):
        """ Add an operator to the currently selected workflow """
        if self.product.isValid():
            selectionModel = self.productExplorer.selectionModel()
            currentIndex = selectionModel.currentIndex()
            node = self.product.itemFromIndex(currentIndex)
            if node is not None:
                nodeType = node.node_type
                if nodeType == NodeType.WORKFLOW:
                    task_selector = TaskSelector(Operators, self)
                    task_selector.setWindowTitle("Task list")
                    task_selector.exec()
                    operator = task_selector.get_selected_task()
                    node.add_operator(operator)
                    self.productExplorer.expandAll()
                    logger.info("New Operator is added")

    def showConfig(self):
        """ Show the application config """
        if not self.configIsOpen:
            configTable = QTableView()
            centralWidget = self.centralWidget()
            self.configTabIndex = centralWidget.addTab(configTable, "Config")

            config = {}
            with open("config.yaml") as f:
                config = yaml.safe_load(f)
            logger.info(config)

            configTableModel = QStandardItemModel(len(config), 2)
            for r, (k,v) in enumerate(config.items()):
                configTableModel.setItem(r,0,QStandardItem(k))
                configTableModel.setItem(r,1,QStandardItem(v))

            configTable.setModel(configTableModel)
            self.configIsOpen = True

if __name__ == "__main__":
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    splash_img = QPixmap("icons/splash.png")
    splash = QSplashScreen(splash_img, Qt.WindowStaysOnTopHint)
    splash.show()

    meta = MetaData()
    products_tbl = Table('products', meta,
            Column('id', Integer, primary_key=True),
            Column('product', String))
    mru_tbl = Table('mru', meta,
            Column('id', Integer, primary_key=True),
            Column('product_id', Integer))
    meta.create_all(db)

    mainWindow = MainWindow()
    mainWindow.setWindowIcon(QIcon(":/icons/logo.png"))
    mainWindow.show()

    splash.finish(mainWindow)
    sys.exit(app.exec_())
