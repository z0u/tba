
# ------------------------------------------------------------------------------
# Navigation

def move_to(n, p, node):

    import tba
    import bge

    if not p.root.ob.get("use_move", False):
        return "You can't move {name}".format(name=p.root.ob.name)

    sce = bge.logic.getCurrentScene()
    new_view = tba.render.nearest_view(node.ob, sce.objects)

    #~ if not new_view or not tba.waypoints.is_validpath(sce.active_camera, new_view):
    #~     return "there is no way to get to the {name}".format(name=node.ob.name)

    if not new_view or not tba.waypoints.is_validpath(p.root.ob, node.ob):
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

    if not node.ob.get("use_alive", False):
        return "You can't embody {name}".format(name=node.ob.name)

    if (node.ob.worldPosition - p.root.ob.worldPosition).length > tba.render.GLOBAL_FAR:
        return "{name} is too far off to embody".format(name=node.ob.name.title())

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


def eat_node(n, p, node):
    import bge
    import tba

    # Eating can move the object!
    prefix = node.ob.name.split(".")[0]

    # BEVER -> EATS -> TREE
    if "tree" in prefix.lower():
        print("WTF?",  p.root.ob.name)
        if "beaver" not in p.root.ob.name.lower():
            return "You nibble the tree but obviously you dont have big enough teeth"


        search = "_{prefix}.eat".format(prefix=prefix)

        sce = bge.logic.getCurrentScene()
        # TODO (multiple?)
        ob = sce.objects.get(search)
        if ob:
            node.ob.worldPosition = ob.worldPosition

            ok = tba.waypoints.conntect_by_position(ob.worldPosition)
            assert(ok)

            return "You have eaten the {name} falls across the river".format(name=node.ob.name)

    return "You cant eat {name} {A}".format(name=node.ob.name, A=search)
