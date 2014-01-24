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


class Tree:
    '''
    A spatial hierarchy of objects.
    '''

    def __init__(self, ref, obs):
        self.root = Node(ref, None)
        self.nodes = {ref: self.root}
        self.build(obs)

    def build(self, obs):
        used_obs = {self.root.ob}
        obs = list(obs)
        obs.sort(key=importance_key(self.root.ob), reverse=True)
        print(obs)
        # Super-nasty O(n^2) operation! Could do this using mathutils.kdtree, but
        # what if we decide the nearest rule isn't good enough? If we stick with
        # nearest, then this should be updated to use kdtree.
        obs2 = list(obs)
        obs2.append(self.root.ob)
        for ob in obs:
            obs2.sort(key=importance_key(ob), reverse=True)
            print(obs2)
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

    def prettyprint(self):
        def _pp(node, indent):
            print(indent + node.ob.name)
            for c in node.children:
                _pp(c, indent + '\t')
        _pp(self.root, '')


class Node:
    def __init__(self, ob, parent):
        self.ob = ob
        self.parent = parent
        self.children = []


class Renderer:
    '''
    Generates a textual description of the scene. This object maintains a
    state, which allows it to generate text with context.
    '''

    def __init__(self):
        self.recent_obs = {}
        sce = bge.logic.getCurrentScene()
        self.available_obs = [ob for ob in sce.objects if
                              ob.visible and
                              ob.groupMembers is None and
                              ob.__class__.__name__ not in {'KX_Camera'}]

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

    def dereference(self, ob_or_name):
        if isinstance(ob_or_name, str):
            return bge.logic.getCurrentScene().objects[ob_or_name]
        else:
            return ob_or_name

    def describe_scene(self):
        sce = bge.logic.getCurrentScene()
        you = sce.objects['you']

        tree = Tree(you, self.available_obs)
        tree.prettyprint()

        self.available_obs.sort(key=importance_key(you), reverse=True)
        hitob, _, _ = you.rayCast(
            you.worldPosition - mathutils.Vector((0, 0, 100)),
            you.worldPosition,
            100)

        if hitob is not None:
            yield sentence('{sub} are standing on {a} {ob}.'.format(
                sub=you.name, a=self.article(hitob), ob=hitob.name))
            self.recent_obs[hitob.name] = hitob

        for ob in self.available_obs:
            if ob is you:
                continue
            yield self.describe_object(ob)

    def describe_object(self, ob_or_name):
        ob = self.dereference(ob_or_name)
        neighbour = nearest(ob, self.available_obs)
        a1 = self.article(ob)
        a2 = self.article(neighbour)
        self.mention(ob)
        self.mention(neighbour)
        return sentence('{a} {ob} is near {a2} {ob2}.'.format(
            a=a1, ob=ob.name,
            a2=a2, ob2=neighbour))

def render(c):
    r = Renderer()
    for sentence in r.describe_scene():
        print(sentence)
