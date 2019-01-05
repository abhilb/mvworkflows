from PyQt5.QtWidgets import *

HEIGHT = 120
WIDTH = 200
GAP = 200


class WorkflowMap(QGraphicsView):
    """
    A map to show the interconnection between the operators in a workflow
    """
    def __init__(self, parent = None):
        super().__init__(parent)

        self._scene = QGraphicsScene()
        self.setScene(self._scene)

    def set_workflow(self, wf):
        top = self._scene.sceneRect().top()
        left = self._scene.sceneRect().left()

        num_of_operators = wf.rowCount()
        for row in range(num_of_operators):
            op = wf.child(row)
            self._scene.addRect( left + row * WIDTH + GAP, top + 200, WIDTH, HEIGHT)
