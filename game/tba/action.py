
# ------------------------------------------------------------------------------
# Navigation

def _parse_nodegraph(ob):
    me = ob.meshes[0]

    # find unique vertices
    vdict = {}
    verts_new = []
    nvert = me.getVertexArrayLength(0)
    verts_orig = [None] * nvert
    verts_map = [-1] * nvert
    for i in range(nvert):
        v_vec = me.getVertex(0, i).XYZ
        v = v_vec.to_tuple(3)
        verts_orig[i] = v
        iv = vdict.get(v)
        if iv is not None:
            verts_map[i] = iv
        else:
            iv = len(vdict)
            vdict[v] = iv
            verts_new.append(v_vec.copy())
        verts_map[i] = iv

    verts = [None] * len(vdict)
    verts_link = [[] for i in range(len(vdict))]
    for k, v in vdict.items():
        verts[v] = k

    npoly = me.numPolygons
    for i in range(npoly):
        p = me.getPolygon(i)
        v = [verts_map[v] for v in (p.v1, p.v2, p.v3, p.v4)]
        for i in range(4):
            a, b  = v[i], v[i - 1]
            if a != b:
                verts_link[a].append(b)
                verts_link[b].append(a)

    return verts_new, verts_link


def _is_validpath(ob_a, ob_b):
    import tba

    verts_new, verts_link = tba.prompt.globals["WAYPOINTS"]

    def close_point(pt, limit=5.0):
        cos = [(i, co) for i, co in enumerate(verts_new)]
        cos.sort(key=lambda v: (v[1] - pt).length)
        length = (cos[0][1] - pt).length
        if length < limit:
            return cos[0][0]
        else:
            return -1

    i_a = close_point(ob_a.worldPosition.copy())
    i_b = close_point(ob_b.worldPosition.copy())

    if -1 in (i_a, i_b):
        print("NOT ON PATH")
        return False

    if i_a == i_b:
        print("FOUND THE SAME?")
        # odd case
        return True


    def others(i, ignore):
        return [j for j in verts_link[i] if j not in ignore]

    visited = set()

    to_search = [i_a]

    while to_search:
        i = to_search.pop()
        visited.add(i)
        for j in others(i, visited):
            if j == i_b:
                return True
            to_search.append(j)
    return False


def move_to(n, p, node):

    import tba
    import bge

    sce = bge.logic.getCurrentScene()
    new_view = tba.render.nearest_view(node.ob, sce.objects)

    if not new_view or not _is_validpath(sce.active_camera, new_view):
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

