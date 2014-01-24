import bge
import mathutils


def write_sentence(text):
    print(text[0].upper() + text[1:])


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

    def importance_key(self, ob):
        return p(ob, 'size', 1.0) * p(ob, 'rel_size', 1.0)

    def describe_scene(self):
        sce = bge.logic.getCurrentScene()
        scene_obs = list(sce.objects)
        scene_obs.sort(key=self.importance_key, reverse=True)

        you = sce.objects['you']
        hitob, _, _ = you.rayCast(
            you.worldPosition - mathutils.Vector((0, 0, 100)),
            you.worldPosition,
            100)

        if hitob is not None:
            write_sentence('{sub} are standing on {a} {ob}'.format(
                sub=you.name, a=self.article(hitob), ob=hitob.name))
            self.recent_obs[hitob.name] = hitob

        for ob in scene_obs:
            if ob is you:
                continue
            neighbour = nearest(ob, scene_obs)
            write_sentence('{a} {ob} is near {a2} {ob2}'.format(
                a=self.article(ob), ob=ob.name,
                a2=self.article(neighbour), ob2=neighbour))
            self.mention(ob)
            self.mention(neighbour)

def render(c):
    r = Renderer()
    r.describe_scene()
