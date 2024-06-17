from qt_node_graph.core.bases.base_node import _BaseNode

class SinglePivot(_BaseNode):
    def __init__(self, name):
        super().__init__(name)

def create_node(name="single_pivot"):
    return SinglePivot(name=name)