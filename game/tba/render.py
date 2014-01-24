import bge
import mathutils

def p(ob, prop, default=None):
    '''Fetches a game object property; can return default value'''
    try:
        return ob[prop]
    except KeyError:
        return default

class Renderer:
    def __init__(self):
        self.recent_obs = {}

    def mention(self, ob):
        self.recent_obs[ob.name] = ob

    def is_definite_article(self, ob):
        return ob.name in self.recent_obs and self.recent_obs[ob.name] is ob

    def article(self, ob):
        if self.is_definite_article(ob):
            # Object has been mentioned recently.
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
        obs = list(sce.objects)
        obs.sort(key=self.importance_key, reverse=True)

        you = sce.objects['You']
        hitob, _, _ = you.rayCast(
            you.worldPosition - mathutils.Vector((0, 0, 100)),
            you.worldPosition,
            100)

        if hitob is not None:
            print('{sub} are standing on {a} {ob}'.format(
                sub=you.name, a=self.article(hitob), ob=hitob.name))
            self.recent_obs[hitob.name] = hitob

        for ob in sce.objects:
            if ob is you:
                continue
            print('There is {a} {ob}'.format(
                a=self.article(ob), ob=ob.name))
            self.recent_obs[ob.name] = ob

def render(c):
    r = Renderer()
    r.describe_scene()
