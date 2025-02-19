from genesis.core.bases import base_node
from genesis.core.objects import attributes

import importlib
importlib.reload(base_node)
importlib.reload(attributes)

class GroupNode(base_node.Node):
    def __init__(self, name="group", value="", parent=None):
        super().__init__(name, parent=parent)

        self._COLOR = attributes.FloatRGBA(name="color")
    
    @property
    def color(self):
        return self._COLOR

class StringNode(base_node.Node):
    def __init__(self, name="string", value="", parent=None):
        super().__init__(name, parent=parent)

        self._INPUT = attributes.String(name="input", value=value)
        self.add_input(self.input)

        self._OUTPUT = attributes.String(name="output", value=value, locked=True, hidden=True)
        self.add_output(self.output)

        self.input.value_changed.connect(self.compute)
        self.compute()

    @property
    def input(self):
        return self._INPUT

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            self.output.set(self.input.get(), force=True)
            self.computed.emit()

class FloatNode(base_node.Node):
    def __init__(self, name="float", value=0.0, parent=None):
        super().__init__(name, parent=parent)

        self._INPUT = attributes.Float(name="input", value=value)
        self.add_input(self.input)

        self._OUTPUT = attributes.Float(name="output", value=value, locked=True, hidden=True)
        self.add_output(self.output)

        self.input.value_changed.connect(self.compute)
        self.compute()

    @property
    def input(self):
        return self._INPUT

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            self.output.set(self.input.get(), force=True)
            self.computed.emit()

class IntegerNode(base_node.Node):
    def __init__(self, name="integer", value=0, parent=None):
        super().__init__(name, parent=parent)

        self._INPUT = attributes.Integer(name="input", value=value)
        self.add_input(self.input)

        self._OUTPUT = attributes.Integer(name="output", value=value, locked=True, hidden=True)
        self.add_output(self.output)

        self.input.value_changed.connect(self.compute)
        self.compute()

    @property
    def input(self):
        return self._INPUT

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            self.output.set(self.input.get(), force=True)
            self.computed.emit()

class BooleanNode(base_node.Node):
    def __init__(self, name="boolean", value=False, parent=None):
        super().__init__(name, parent=parent)

        self._INPUT = attributes.Bool(name="input", value=value)
        self.add_input(self.input)

        self._OUTPUT = attributes.Bool(name="output", value=value, locked=True, hidden=True)
        self.add_output(self.output)

        self.input.value_changed.connect(self.compute)
        self.compute()

    @property
    def input(self):
        return self._INPUT

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            self.output.set(self.input.get(), force=True)
            self.computed.emit()

class MathNode(base_node.Node):
    def __init__(self, name="math", value=0.0, parent=None):
        super().__init__(name, parent=parent)
        self._INPUTS = []

        self._FUNCTION = attributes.Enum(name="function", value="add", options=["add", "subtract", "multiply", "divide", "average"])
        self.add_attribute(self.function)

        self.add_input_attr(compute=False)
        self.add_input_attr(compute=False)

        self.function.value_changed.connect(self.compute)

        self._OUTPUT = attributes.Float(name="output", value=value, locked=True, hidden=True)
        self.add_output(self.output)

        self.compute()

    @property
    def output(self):
        return self._OUTPUT

    @property
    def function(self):
        return self._FUNCTION

    def add_input_attr(self, value=0.0, compute=True):
        idx = len(self.inputs)
        attr = attributes.Float(name=f"input[{idx}]", value=value)
        self.add_input(attr)
        attr.value_changed.connect(self.compute)
        if compute:
            self.compute()

    def compute(self):
        if self.update.get():
            input_values = []
            for attr in self.inputs:
                input_values.append(attr.get())

            if self.function.get() == "add":
                value = sum(input_values)

            if self.function.get() == "subtract":
                value = self.inputs[0].get()
                for input_value in input_values[1:]:
                    value -= input_value

            if self.function.get() == "multiply":
                value = self.inputs[0].get()
                for input_value in input_values[1:]:
                    value *= input_value

            if self.function.get() == "divide":
                value = self.inputs[0].get()
                for input_value in input_values[1:]:
                    value /= input_value

            if self.function.get() == "average":
                value = sum(input_values) / len(input_values)

            self.output.set(value, force=True)
            self.computed.emit()

class VectorNode(base_node.Node):
    def __init__(self, name="vector", parent=None):
        super().__init__(name, parent=parent)
        self._INPUT_A = attributes.FloatVector3(name="inputA")
        self._INPUT_B = attributes.FloatVector3(name="inputB")
        self._OUTPUT = attributes.FloatVector3(name="output")
        self.add_input(self.inputA)
        self.add_input(self.inputB)
        self.add_output(self.output)

        self._FUNCTION = attributes.Enum(name="function", value="add", options=["add", "subtract", "multiply", "divide"])
        self.add_attribute(self.function)

        self.inputA.value_changed.connect(self.compute)
        self.inputB.value_changed.connect(self.compute)
        self.function.value_changed.connect(self.compute)

        self.compute()

    @property
    def inputA(self):
        return self._INPUT_A

    @property
    def inputB(self):
        return self._INPUT_B

    @property
    def function(self):
        return self._FUNCTION

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            if self.function.get() == "add":
                x = self.inputA.x.get() + self.inputB.x.get()
                y = self.inputA.y.get() + self.inputB.y.get()
                z = self.inputA.z.get() + self.inputB.z.get()
            if self.function.get() == "subtract":
                x = self.inputA.x.get() - self.inputB.x.get()
                y = self.inputA.y.get() - self.inputB.y.get()
                z = self.inputA.z.get() - self.inputB.z.get()
            if self.function.get() == "multiply":
                x = self.inputA.x.get() * self.inputB.x.get()
                y = self.inputA.y.get() * self.inputB.y.get()
                z = self.inputA.z.get() * self.inputB.z.get()
            if self.function.get() == "divide":
                x = self.inputA.x.get() / self.inputB.x.get()
                y = self.inputA.y.get() / self.inputB.y.get()
                z = self.inputA.z.get() / self.inputB.z.get()
            self.output.set(x, y, z, force=True)
            self.computed.emit()

class ComparisonNode(base_node.Node):
    def __init__(self, name="comparison", parent=None):
        super().__init__(name, parent=parent)
        self._INPUT_A = attributes.FloatVector3(name="inputA")
        self._INPUT_B = attributes.FloatVector3(name="inputB")
        self._OUTPUT = attributes.FloatVector3(name="output")
        self.add_input(self.inputA)
        self.add_input(self.inputB)
        self.add_output(self.output)

        self._FUNCTION = attributes.Enum(name="function", value="equal", options=["equal", "not", "greater", "lesser", "greaterEqual", "lesserEqual"])
        self.add_attribute(self.function)

        self.inputA.value_changed.connect(self.compute)
        self.inputB.value_changed.connect(self.compute)
        self.function.value_changed.connect(self.compute)

        self.compute()

    @property
    def inputA(self):
        return self._INPUT_A

    @property
    def inputB(self):
        return self._INPUT_B

    @property
    def function(self):
        return self._FUNCTION

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            if self.function.get() == "equal":
                x = True if self.inputA.x.get() == self.inputB.x.get() else False
                y = True if self.inputA.y.get() == self.inputB.y.get() else False
                z = True if self.inputA.z.get() == self.inputB.z.get() else False
            if self.function.get() == "not":
                x = True if self.inputA.x.get() != self.inputB.x.get() else False
                y = True if self.inputA.y.get() != self.inputB.y.get() else False
                z = True if self.inputA.z.get() != self.inputB.z.get() else False
            if self.function.get() == "greater":
                x = True if self.inputA.x.get() > self.inputB.x.get() else False
                y = True if self.inputA.y.get() > self.inputB.y.get() else False
                z = True if self.inputA.z.get() > self.inputB.z.get() else False
            if self.function.get() == "lesser":
                x = True if self.inputA.x.get() < self.inputB.x.get() else False
                y = True if self.inputA.y.get() < self.inputB.y.get() else False
                z = True if self.inputA.z.get() < self.inputB.z.get() else False
            if self.function.get() == "greaterEqual":
                x = True if self.inputA.x.get() >= self.inputB.x.get() else False
                y = True if self.inputA.y.get() >= self.inputB.y.get() else False
                z = True if self.inputA.z.get() >= self.inputB.z.get() else False
            if self.function.get() == "lesserEqual":
                x = True if self.inputA.x.get() <= self.inputB.x.get() else False
                y = True if self.inputA.y.get() <= self.inputB.y.get() else False
                z = True if self.inputA.z.get() <= self.inputB.z.get() else False
            self.output.set(x, y, z, force=True)
            self.computed.emit()

class BlendNode(base_node.Node):
    def __init__(self, name="blend", parent=None):
        super().__init__(name, parent=parent)
        self._INPUT_A = attributes.FloatVector3(name="inputA")
        self._INPUT_B = attributes.FloatVector3(name="inputB")
        self._OUTPUT = attributes.FloatVector3(name="output")
        self.add_input(self.inputA)
        self.add_input(self.inputB)
        self.add_output(self.output)

        self._BLEND = attributes.Float(name="blend", min=0.0, max=1.0)
        self.add_input(self.blend)

        self.inputA.value_changed.connect(self.compute)
        self.inputB.value_changed.connect(self.compute)
        self.blend.value_changed.connect(self.compute)

        self.compute()

    @property
    def inputA(self):
        return self._INPUT_A

    @property
    def inputB(self):
        return self._INPUT_B

    @property
    def blend(self):
        return self._BLEND

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            x = (self.inputA.x.get() + self.inputB.x.get()) / 2.0
            y = (self.inputA.y.get() + self.inputB.y.get()) / 2.0
            z = (self.inputA.z.get() + self.inputB.z.get()) / 2.0
            self.output.set(x, y, z, force=True)
            self.computed.emit()

class ScriptNode(base_node.Node):
    def __init__(self, name="script", value="", parent=None):
        super().__init__(name, parent=parent)

        self._INPUT = attributes.String(name="input", value=value)
        self.add_input(self.input)

        self._OUTPUT = attributes.String(name="output", value=value, locked=True, hidden=True)
        self.add_output(self.output)

        self.input.value_changed.connect(self.compute)
        self.compute()

    @property
    def input(self):
        return self._INPUT

    @property
    def output(self):
        return self._OUTPUT

    def compute(self):
        if self.update.get():
            try:
                exec(self.input.get())
                self.output.set(self.input.get(), force=True)
                self.computed.emit()
            except:
                self.output.set("", force=True)

class TransformNode(base_node.Node):
    def __init__(self, name="transform", parent=None):
        super().__init__(name, parent=parent)
        self._TRANSLATE = attributes.FloatVector3(name="translate")
        self._ROTATE = attributes.FloatVector3(name="rotate")
        self._SCALE = attributes.FloatVector3(name="scale")
        self.add_input(self.translate)
        self.add_input(self.rotate)
        self.add_input(self.scale)

        self._OUTPUT = attributes.Matrix(name="output")
        self.add_output(self.output)

        self._INPUT = [self.translate, self.rotate, self.scale]

        self.translate.value_changed.connect(self.compute)
        self.rotate.value_changed.connect(self.compute)
        self.scale.value_changed.connect(self.compute)

        self.compute()

    @property
    def input(self):
        return self._INPUT

    @property
    def output(self):
        return self._OUTPUT

    @property
    def translate(self):
        return self._TRANSLATE

    @property
    def rotate(self):
        return self._ROTATE

    @property
    def scale(self):
        return self._SCALE

    def compute(self):
        if self.update.get():
            translate = [self.translate.x.get(), self.translate.y.get(), self.translate.z.get()]
            rotate = [self.rotate.x.get(), self.rotate.y.get(), self.rotate.z.get()]
            scale = [self.scale.x.get(), self.scale.y.get(), self.scale.z.get()]
            self.output.set(translate, rotate, scale)
            self.computed.emit()



def get_nodes():
    return {"group": GroupNode,
            "string": StringNode,
            "float": FloatNode,
            "integer": IntegerNode,
            "bool": BooleanNode,
            "math": MathNode,
            "vector": VectorNode,
            "compare": ComparisonNode,
            "blend": BlendNode,
            "script": ScriptNode,
            "transform": TransformNode}

def create_node(node, name=""):
    if name:
        return get_nodes()[node](name=name)
    else:
        return get_nodes()[node]()