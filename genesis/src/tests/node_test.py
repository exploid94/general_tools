from genesis.core.objects import nodes

n = nodes.TransformNode()

n.output.value_changed.connect(lambda: print(n.output.value))

n.rotate.set(0.0, 1.0, 2.0)
