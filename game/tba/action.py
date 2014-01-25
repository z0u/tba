
# ------------------------------------------------------------------------------
# Navigation

def move_to():
    pass


# ------------------------------------------------------------------------------
# Object

def embody_node(n, p, node):
    p.root = node
    return "You have embodied the {name}".format(name=node.ob.name)


def open_node():
    pass


def close_node():
    pass


def inspect_node(n, p, node):
    return n.describe_node(node)

