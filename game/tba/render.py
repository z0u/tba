import bge
import mathutils
import difflib


def sentence(text):
    return text[0].upper() + text[1:]


def p(ob, prop, default=None):
    '''Fetches a game object property; can return default value'''
    try:
        return ob[prop]
    except KeyError:
        return default


def has_mesh(ob):
    return len(ob.meshes) > 0


def vert_num(ob):
    me = ob.meshes[0]
    n = 0
    for m_i in range(len(me.materials)):
        n += me.getVertexArrayLength(m_i)
    return n


def vert_iter(ob):
    me = ob.meshes[0]
    for m_i in range(len(me.materials)):
        for v_i in range(me.getVertexArrayLength(m_i)):
            yield me.getVertex(m_i, v_i)


def kd(ob):
    if '_kdtree' in ob:
        return ob['_kdtree']

    if not has_mesh(ob):
        # No mesh; just use one "vertex" at the centre.
        tree = mathutils.kdtree.KDTree(1)
        tree.insert((0, 0, 0), 0)
    else:
        n = vert_num(ob)
        verts = {tuple(v.XYZ) for v in vert_iter(ob)}
        # Add all vertices plus one at the centre.
        tree = mathutils.kdtree.KDTree(n + 1)
        tree.insert((0, 0, 0), 0)
        for i, v in enumerate(verts):
            tree.insert(v, i)

    tree.balance()
    ob['_kdtree'] = tree
    return tree


_search_vecs = []


def search_vecs():
    if len(_search_vecs) > 0:
        return _search_vecs
    sce = bge.logic.getCurrentScene()
    space = sce.objects['_SearchSpace']
    # Transform into tuples to allow hashing in a set.
    verts = {tuple(v.XYZ) for v in vert_iter(space)}
    # Transform back into a list of vectors.
    _search_vecs.extend(mathutils.Vector(v) for v in verts)
    return _search_vecs


def closest_point(ob, ref):
    pos_from = ref.worldPosition
    if not has_mesh(ob):
        vec = pos_from - ob.worldPosition
        vec.magnitude = p(ob, 'size', 1.0)
        co = ob.worldPosition + vec
        return co, (co - pos_from).magnitude

    closest = None
    min_dist = 0.0
    # Search everywhere!
    for vec in search_vecs():
        pos_through = pos_from + vec
        for hitob, co, nor in rayCastIterate(
            pos_through, ref, co_from=pos_from, dist=100):
            if hitob is not ob:
                continue
            dist = (pos_from - co).magnitude
            if closest is None or dist < min_dist:
                closest = co
                min_dist = dist

    if closest is not None:
        return closest, min_dist

    # Fall back to KD tree search for nearest verts...
    mat = ob.worldTransform
    mat_inv = mat.inverted()
    ref_pos = mat_inv * ref.worldPosition
    co, i, dist = kd(ob).find(ref_pos)

    co = mat * co
    dist *= mat.median_scale
    return co, dist


class distance_key:
    '''For sorting objects based on distance from a reference point.'''
    def __init__(self, ref):
        self.ref = ref
        self.ref_pos = self.ref.worldPosition

    def __call__(self, ob):
        return (self.ref_pos - ob.worldPosition).magnitude


class importance_key:
    '''
    For sorting objects based on apparent importance. Basically, close or large
    objects are more important.
    '''
    def __init__(self, ref):
        self.ref = ref
        self.ref_pos = self.ref.worldPosition

    def __call__(self, ob):
        co, dist = closest_point(ob, self.ref)
        #print("{} -> {}: dist={}, co={}".format(self.ref.name, ob, dist, co))

        # Adjust distance to account for object size (so touching objects have
        # distance of 0).
        dist -= p(self.ref, 'size', 1.0)# + p(ob, 'size', 1.0)
        dist = max(0, dist)
        # Avoid div0
        dist += 1

        #importance = p(ob, 'size', 1.0) * p(ob, 'rel_size', 1.0)
        importance = p(ob, 'rel_size', 1.0)

#        print(ob, dist, importance)
        return importance / (dist * dist)


def nearest(ob, obs):
    obs = list(obs)
    obs.sort(key=distance_key(ob))
    for other in obs:
        if other is not ob:
            return other
    return None


def nearest_view(ob, obs):
    obs = [o for o in obs if o.__class__.__name__ == 'KX_Camera']
    loc = ob.worldPosition
    obs.sort(key=lambda o: (loc - o.worldPosition).length)
    for other in obs:
        # check if we can use?
        return other


def rayCastIterate(ob_to, ob_from, co_from=None, dist=0, prop='', face=0, xray=0, poly=0):
    if co_from is None:
        co_from = ob_from.worldPosition

    if hasattr(ob_to, 'worldPosition'):
        co_to = ob_to.worldPosition
    else:
        co_to = ob_to

    vec = co_to - co_from
    vec.normalize()
    epsilon = vec * 0.001
    co_from -= epsilon
    while True:
        #print(co_to, co_from, epsilon)
        ob, co, nor = ob_from.rayCast(co_to, co_from, dist, prop, face, xray, poly)
        if ob is None:
            break
        yield ob, co, nor
        co_from = co + epsilon
        if vec.dot(co_to - co_from) < 0:
            break


def visibility(ob, ref, limit=0.01):
    vis = 1.0
    for hitob, co, nor in rayCastIterate(ob, ref):
        if hitob is ob:
            return vis
        if hitob is None:
            # In this case, we've reached the centre of a meshless object.
            return vis
        vis *= 1.0 - p(hitob, 'opacity', 1.0)
        if vis < limit:
            break
    return vis


class Perspective:
    '''
    A spatial hierarchy of objects.
    '''

    def __init__(self, ref, obs=None):
        if obs is None:
            sce = bge.logic.getCurrentScene()
            obs = []
            for ob in sce.objects:
                if not ob.visible:
                    continue
                if ob.name.startswith('_'):
                    continue
                if ob.groupMembers is not None:
                    continue
                if ob.__class__.__name__ == 'KX_Camera':
                    if ob is not sce.active_camera:
                        continue
                obs.append(ob)

        self.root = Node(ref, None)
        self.nodes = {ref: self.root}

        used_obs = {self.root.ob}
        obs = list(obs)
        obs.sort(key=importance_key(self.root.ob), reverse=True)
        # Super-nasty O(n^2) operation! Could do this using mathutils.kdtree, but
        # what if we decide the nearest rule isn't good enough? If we stick with
        # nearest, then this should be updated to use kdtree.
        obs2 = list(obs)
        obs2.append(self.root.ob)
        for ob in obs:
            if ob in self.nodes:
                continue

            # Ensure object is visible. Should look at each vertex? Currently
            # just checks centroids.
            if visibility(ob, self.root.ob) < 0.01:
                continue

            obs2.sort(key=importance_key(ob), reverse=True)
            for ob2 in obs2:
                if ob2 in self.nodes:
                    self.add(ob, ob2)
                    break

    def add(self, ob, parent):
        pnode = self.nodes[parent]
        node = Node(ob, pnode)
        pnode.children.append(node)
        self.nodes[ob] = node
        return node

    def get_node(self, ob_or_name):
        # TODO: extend to allow fuzzy matching.
        if isinstance(ob_or_name, str):
            ob = bge.logic.getCurrentScene().objects[ob_or_name]
        return self.nodes[ob]

    def get_node_fuzzy(self, name):
        # Exact match first.
        for ob in self.nodes.keys():
            if ob.name.lower() == name.lower():
                return self.nodes[ob]

        # No exact match; now fuzzy match!
        best_ratio = 0.0
        second_best_ratio = 0.0
        best_ob = None
        for ob in self.nodes.keys():
            ratio = difflib.SequenceMatcher(None, name, ob.name).ratio()
            if ratio > best_ratio:
                second_best_ratio = best_ratio
                best_ob = ob
                best_ratio = ratio
        if best_ratio < 0.4:
            raise KeyError("%s can't be found." % name)
        if best_ratio - 0.05 < second_best_ratio:
            raise KeyError("%s is ambiguous. Please be more specific." % name)
        return self.nodes[best_ob]

    def prettyprint(self):
        def _pp(node, indent):
            print("%s%s" % (indent, node.ob.name))
            for c in node.children:
                _pp(c, indent + '\t')
        _pp(self.root, '')

    def walk(self):
        def _walk(node):
            yield node
            for c in node.children:
                yield from _walk(c)
        yield from _walk(self.root)


class Node:
    def __init__(self, ob, parent):
        self.ob = ob
        self.parent = parent
        self.children = []


class Narrator:
    '''
    Generates a textual description of the scene. This object maintains a
    state, which allows it to generate text with context.
    '''

    def __init__(self):
        self.recent_obs = {}

    def mention(self, ob):
        self.recent_obs[ob.name] = ob

    def is_definite_article(self, ob):
        return ob.name in self.recent_obs and self.recent_obs[ob.name] is ob

    def article(self, ob):
        if self.is_definite_article(ob):
            return 'the'
        else:
            if ob.name[0] in 'aeio':
                return 'an'
            else:
                return 'a'

    def nounphrase(self, ob):
        sce = bge.logic.getCurrentScene()
        if ob is sce.active_camera:
            return 'you'

        return '{a} {ob}'.format(a=self.article(ob), ob=ob.name)

    def preposition(self, ob, ref):
        ## First, special case for objects that are inside!
        #vec = ob.worldPosition - ref.worldPosition
        #dist = vec.magnitude - p(ref, 'size', 1.0)
        #if dist < 0:
        #    return "in"

        # Now look at the surface of the target object.
        co, dist = closest_point(ref, ob)
        print(ref, ob, co, dist)
        vec = ob.worldPosition - co
        #dist = vec.magnitude - p(ref, 'size', 1.0)

        # For over/under, check dot product first.
        # TODO: this stuff should be incorporated into the perspective tree
        # builder to generate better trees.
        dot = vec.normalized().dot((0,0,1))
        print(ob, ref, dot, vec)
        if abs(dot) > 0.9:
            if vec.z > 2.0:
                return "over"
            elif vec.z > 0.0:
                return "on"
            elif vec.z < 0.0:
                return "under"

        if dist < 2.0:  # 1.0 would be strict but 2.0 is ok
            return "next to"
        else:
            return "near"

    def describe_scene(self, tree):
        actor = tree.root.ob
        ground, _, _ = actor.rayCast(
            actor.worldPosition - mathutils.Vector((0, 0, 100)),
            actor.worldPosition,
            100)

        if ground is not None:
            yield sentence('{sub} are standing on {a} {ob}.'.format(
                sub=self.nounphrase(actor), a=self.article(ground),
                ob=ground.name))
            self.recent_obs[ground.name] = ground

        for node in tree.walk():
            if node is tree.root:
                continue
            yield self.describe_node_loc(node)

    def describe_node(self, node):
        ob = node.ob
        if 'description' in ob:
            text = ob['description']
        else:
            text = "It's just {ob}.".format(ob=self.nounphrase(ob))
        self.mention(ob)
        return text

    def describe_node_loc(self, node):
        ob = node.ob
        ref = node.parent.ob
        text = sentence('{s} is {prep} {ob}.'.format(
            s=self.nounphrase(ob), prep=self.preposition(ob, ref),
            ob=self.nounphrase(ref)))
        self.mention(ob)
        self.mention(ref)
        return text


def test(c):
    sce = bge.logic.getCurrentScene()
    p = Perspective(sce.active_camera)
    p.prettyprint()
    n = Narrator()
    for sentence in n.describe_scene(p):
        print(sentence)

    #print()
    #print(n.describe_node(p.get_node('monkey')))
