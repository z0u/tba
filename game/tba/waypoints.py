def parse_nodegraph(ob):
    me = ob.meshes[0]

    # find unique vertices
    vdict = {}
    verts_new = []
    nvert = me.getVertexArrayLength(0)
    verts_map = [-1] * nvert
    for i in range(nvert):
        v_vec = me.getVertex(0, i).XYZ
        v = v_vec.to_tuple(3)
        iv = vdict.get(v)
        if iv is None:
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


def close_point_list(pt, limit=2.0, id_str="<UNKNOWN>"):
    import tba
    verts_new, verts_link = tba.prompt.globals["WAYPOINTS"]
    cos = [(i, co) for i, co in enumerate(verts_new)]
    cos.sort(key=lambda v: (v[1] - pt).xy.length)
    length = (cos[0][1] - pt).xy.length
    if length < limit:
        print("length %s < limit=%r:" % (id_str, limit), length)
        return cos
    else:
        return []


def close_point(pt, limit=2.0, id_str="<UNKNOWN>"):
    cos = close_point_list(pt, limit, id_str)
    if cos:
        return cos[0][0]
    else:
        return -1


def is_validpath(ob_a, ob_b):
    import tba

    verts_new, verts_link = tba.prompt.globals["WAYPOINTS"]

    i_a = close_point(ob_a.worldPosition.copy(), id_str=ob_a.name)
    i_b = close_point(ob_b.worldPosition.copy(), id_str=ob_b.name)

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


def connext_by_index(a, b):
    import tba
    verts_new, verts_link = tba.prompt.globals["WAYPOINTS"]
    if a not in verts_link[b]:
        verts_link[b].append(a)
    if b not in verts_link[a]:
        verts_link[a].append(b)


def conntect_by_position(co):
    cos = close_point_list(co, limit=1000.0)
    print(cos)
    if len(cos) >= 2:
        a, b = cos[0][0], cos[1][0]
        connext_by_index(a, b)
        print("WAYPOINT ADDED")
        return True
    else:
        return False

