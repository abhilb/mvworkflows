import pickle
from PyQt5.QtCore import pyqtSignal, QObject

class ChangeManager(QObject):
    """ Manages and undo and redo of product changes """

    index_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.snapshots = []
        self.current_index = -1
        self._ignore = False

    @property
    def ignore_changes(self):
        return self._ignore

    @ignore_changes.setter
    def ignore_changes(self, value):
        self._ignore = value

    def is_undo_possible(self):
        return self.current_index > 0

    def is_redo_possible(self):
        return (len(self.snapshots) - self.current_index) > 1

    def save_state(self, product):
        if self.ignore_changes:
            return

        """ Save the state of product to deque """
        data = pickle.dumps(product.state)
        self.snapshots.append(data)
        self.current_index += 1
        self.index_changed.emit()

    def undo(self, product):
        """ Roll back the state of the product """
        self.current_index -= 1
        if self.current_index >= 0:
            data = pickle.loads(self.snapshots[self.current_index])
            product.state = data
        else:
            self.current_index = -1
        self.index_changed.emit()
        return product

    def redo(self, product):
        self.current_index += 1
        if self.current_index < len(self.snapshots):
            data = pickle.loads(self.snapshots[self.current_index])
            product.state = data
        else:
            self.current_index = len(self.snapshots) - 1
        self.index_changed.emit()
        return product

    def clear(self):
        """ Clear the deque """
        self.snapshots.clear()
