
# ------------------------------------------------------------------------------
# Navigation

def move_to(n, p, node):

    import tba
    import bge

    if not p.root.ob.get("use_move", False):
        text = "{sub} is immobile.".format(sub=n.nounphrase(p.root.ob, p))
        n.mention(p.root.ob)
        return text

    sce = bge.logic.getCurrentScene()
    new_view = tba.render.nearest_view(node.ob, sce.objects)

    #~ if not new_view or not tba.waypoints.is_validpath(sce.active_camera, new_view):
    #~     return "there is no way to get to the {name}".format(name=node.ob.name)

    if not new_view or not tba.waypoints.is_validpath(p.root.ob, node.ob):
        text = "There is no way to get to the {name}".format(name=node.ob.name)
        n.mention(p.root.ob)
        return text


    p.root.ob.worldPosition = new_view.worldPosition

    if new_view:
        sce.active_camera = new_view

    # Re-create perspective using the same object - since the object has now
    # been moved, the resulting tree will be different.
    tba.prompt.globals["PERSPECTIVE"] = tba.render.Perspective(p.root.ob)

    return "You have moved to the {name}".format(name=node.ob.name)


# ------------------------------------------------------------------------------
# Object

def embody_node(n, p, node):
    import tba
    import bge

    if not node.ob.get("use_alive", False):
        text = "{sub} has no spirit to embody.".format(sub=n.nounphrase(node.ob, p))
        n.mention(p.root.ob)
        return text

    if (node.ob.worldPosition - p.root.ob.worldPosition).length > tba.render.GLOBAL_FAR:
        return "{name} is too far off to embody".format(name=node.ob.name.title())

    sce = bge.logic.getCurrentScene()
    new_view = tba.render.nearest_view(node.ob, sce.objects)
    if new_view:
        sce.active_camera = new_view

    tba.prompt.globals["PERSPECTIVE"] = tba.render.Perspective(node.ob)

    if 'element' in node.ob:
        tba.prompt.globals["FONT"] = node.ob['element']
    else:
        tba.prompt.globals["FONT"] = None

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

    return "You cant eat {name}".format(name=n.nounphrase(node.ob, p))


def _inventory(ob):
    return [o for o in ob.children if not o.name.startswith("_")]

def take_node(n, p, node):
    import bge
    import tba

    obs = _inventory(node.ob)

    if obs:
        return "You're holding {name}".format(name=n.nounphrase(obs[0], p))
    else:
        sce = bge.logic.getCurrentScene()
        new_view = tba.render.nearest_view(node.ob, sce.objects)
        if sce.active_camera != new_view:
            return "You're too faw away from {name}".format(name=n.nounphrase(node.ob, p))

        if p.root.ob == node.ob:
            return "Can't take yourself"

        if not node.ob.get("use_collect", False):
            return "You can't take {name}".format(name=n.nounphrase(node.ob, p))

        p.root.ob.setParent(node.ob)
        node.ob.worldPosition = p.root.ob.worldPosition

        return "You take {name}".format(name=n.nounphrase(node.ob, p))

def drop_any(n, p):
    pass
