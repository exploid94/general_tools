import os
_PATH = os.path.dirname(__file__)

def get_all_nodes():
    dict = {}
    for f in os.listdir(_PATH):
        if not f.startswith("__"):
            node_name = f.replace(".py", "")
            dict[node_name] = os.path.join(_PATH, node_name)
    return dict
