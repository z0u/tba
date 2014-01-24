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
        if hasattr(ref, 'worldPosition'):
            self.ref = ref.worldPosition
        else:
            self.ref = ref

    def __call__(self, ob):
        return (self.ref - ob.worldPosition).magnitude


def nearest(ob, obs):
    obs = list(obs)
    obs.sort(key=distance_key(ob))
    for other in obs:
        if other is not ob:
            return other
    return None


class Renderer:
    '''
    Generates a textual description of the scene. This object maintains a
    state, which allows it to generate text with context.
    '''

    def __init__(self):
        self.recent_obs = {}
        sce = bge.logic.getCurrentScene()
        self.available_obs = [ob for ob in sce.objects if
                              ob.visible and ob.groupMembers is None]

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

    def importance_key(self, ob):
        return p(ob, 'size', 1.0) * p(ob, 'rel_size', 1.0)

    def describe_scene(self):
        self.available_obs.sort(key=self.importance_key, reverse=True)
        sce = bge.logic.getCurrentScene()
        you = sce.objects['you']
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
