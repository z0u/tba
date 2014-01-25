
# ------------------------------------------------------------------------------
# Navigation

def _is_validpath(ob_a, ob_b):
    print(ob_a, ob_b)
    def others(ob, ignore):
        others = ob.children[:]
        if ob.parent:
            others.append(ob.parent)
        return [o for o in others if o not in ignore]

    visited = set()

    to_search = [ob_a]

    while to_search:
        ob = to_search.pop()
        visited.add(ob)

        for o in others(ob, visited):
            if o == ob_b:
                return True
            to_search.append(o)
    # build links from parents
    return False



def move_to(n, p, node):

    import tba
    import bge

    sce = bge.logic.getCurrentScene()
    new_view = tba.render.nearest_view(node.ob, sce.objects)

    if not _is_validpath(sce.active_camera, new_view):
        return "There is no way to get to the {name}".format(name=node.ob.name)

    p.root.ob.worldPosition = new_view.worldPosition

    if new_view:
        sce.active_camera = new_view

    tba.prompt.globals["PERSPECTIVE"] = tba.render.Perspective(node.ob)

    return "You have moved to the {name}".format(name=node.ob.name)


# ------------------------------------------------------------------------------
# Object

def embody_node(n, p, node):
    import tba
    import bge

    sce = bge.logic.getCurrentScene()
    new_view = tba.render.nearest_view(node.ob, sce.objects)
    if new_view:
        sce.active_camera = new_view

    tba.prompt.globals["PERSPECTIVE"] = tba.render.Perspective(node.ob)
    #p.root = node
    #p.__init__(p.root.ob)
    embody_descr = node.ob.get("embody_descr", "")
    if embody_descr:
        return embody_descr
    else:
        return "You have embodied the {name}".format(name=node.ob.name)


def open_node():
    pass


def close_node():
    pass


def inspect_node(n, p, node):
    return n.describe_node(node)


def whereis_node(n, p, node):
    return n.describe_node_loc(node)

