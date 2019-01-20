"""
Client worker thread.
"""

from PyQt5.QtCore import QThread, pyqtSignal
import time
import zmq

# Setup logging
import logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level="INFO")
logger = logging.getLogger("[mvwf]")

class ClientWorker(QThread):
    """
    Client Worker Class
    - implments QThread
    """

    completedSignal = pyqtSignal()

    def __init__(self, parent=None):
        """
        Client Worker constructor
        """
        logger.info("Created the client worker objecct")
        super().__init__(parent)
        self.ctx = zmq.Context.instance()
        self.socket = self.ctx.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5556")
        self._result = {}

    @property
    def result(self):
        """
        Return the workflow execution result
        """
        return self._result


    def run(self):
        """
        Run function of the QThread
        """
        logger.info("Starting the client worker")
        self.socket.send_string("start")
        poll_result = self.socket.poll(5000)
        if poll_result == 0:
            logger.info("Timed out")
        else:
            self._result = self.socket.recv_multipart()
        logger.info("Exiting the client worker")
        self.completedSignal.emit()
        self.socket.close()
        self.ctx.destroy()

