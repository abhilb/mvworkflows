import pickle
from collections import deque

class ChangeManager():
    """ Manages and undo and redo of product changes """
    def __init__(self):
        self.snapshots = []
        self.current_index = -1
        self._ignore = False
        print(f"change_manager: current_index: {self.current_index}")

    @property
    def ignore_changes(self):
        return self._ignore

    @ignore_changes.setter
    def ignore_changes(self, value):
        self._ignore = value

    def save_state(self, product):
        if self.ignore_changes:
            return

        """ Save the state of product to deque """
        data = pickle.dumps(product.state)
        self.snapshots.append(data)
        self.current_index += 1
        print(f"change_manager: current_index: {self.current_index}")

    def undo(self, product):
        """ Roll back the state of the product """
        self.current_index -= 1
        if self.current_index >= 0:
            data = pickle.loads(self.snapshots[self.current_index])
            product.state = data
        else:
            self.current_index = -1
        print(f"change_manager: current_index: {self.current_index}")
        return product

    def redo(self, product):
        self.current_index += 1
        if self.current_index < len(self.snapshots):
            data = pickle.loads(self.snapshots[self.current_index])
            product.state = data
        else:
            self.current_index = len(self.snapshots) - 1
        print(f"change_manager: current_index: {self.current_index}")
        return product

    def clear(self):
        """ Clear the deque """
        self.snapshots.clear()
