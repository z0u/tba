import bge
import mathutils


def sentence(text):
    return text[0].upper() + text[1:]


def p(ob, prop, default=None):
    '''Fetches a game object property; can return default value'''
    try:
        return ob[prop]
    except KeyError:
        return default


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
        dist = (self.ref_pos - ob.worldPosition).magnitude
        # Adjust distance to account for object size (so touching objects have
        # distance of 0).
        dist -= p(self.ref, 'size', 1.0) + p(ob, 'size', 1.0)
        dist = max(0, dist)
        # Avoid div0
        dist += 1

        importance = p(ob, 'size', 1.0) * p(ob, 'rel_size', 1.0)

#        print(ob, dist, importance)
        return importance / (dist * dist)


def nearest(ob, obs):
    obs = list(obs)
    obs.sort(key=distance_key(ob))
    for other in obs:
        if other is not ob:
            return other
    return None


class Perspective:
    '''
    A spatial hierarchy of objects.
    '''

    def __init__(self, ref, obs=None):
        if obs is None:
            sce = bge.logic.getCurrentScene()
            obs = [ob for ob in sce.objects if
                   ob.visible and
                   not ob.name.startswith('_') and
                   ob.groupMembers is None and
                   ob.__class__.__name__ not in {'KX_Camera'}]

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

    def prettyprint(self):
        def _pp(node, indent):
            print(indent + node.ob.name)
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

    def describe_scene(self, tree):
        you = tree.root.ob
        ground, _, _ = you.rayCast(
            you.worldPosition - mathutils.Vector((0, 0, 100)),
            you.worldPosition,
            100)

        if ground is not None:
            yield sentence('{sub} are standing on {a} {ob}.'.format(
                sub=self.nounphrase(you), a=self.article(ground),
                ob=ground.name))
            self.recent_obs[ground.name] = ground

        for node in tree.walk():
            if node is tree.root:
                continue
            yield self.describe_node(node)

    def describe_node(self, node):
        ob = node.ob
        ref = node.parent.ob
        sen = sentence('{s} is near {ob}.'.format(
            s=self.nounphrase(ob), ob=self.nounphrase(ref)))
        self.mention(ob)
        self.mention(ref)
        return sen


def test(c):
    sce = bge.logic.getCurrentScene()
    p = Perspective(sce.active_camera)
    n = Narrator()
    for sentence in n.describe_scene(p):
        print(sentence)

    print(n.describe_node(p.get_node('monkey')))
