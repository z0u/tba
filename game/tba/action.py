
# ------------------------------------------------------------------------------
# Navigation

def move_to():
    pass


# ------------------------------------------------------------------------------
# Object

def embody_node(n, p, node):
    import tba

    tba.prompt.globals["PERSPECTIVE"] = tba.render.Perspective(node.ob)
    #p.root = node
    #p.__init__(p.root.ob)
    return "You have embodied the {name}".format(name=node.ob.name)


def open_node():
    pass


def close_node():
    pass


def inspect_node(n, p, node):
    return n.describe_node(node)

