import bge
import mathutils

def p(ob, prop, default=None):
    '''Fetches a game object property; can return default value'''
    try:
        return ob[prop]
    except KeyError:
        return default

def importance_key(ob):
    return p(ob, 'size', 1.0) * p(ob, 'rel_size', 1.0)

def describe_scene(c):
    sce = bge.logic.getCurrentScene()
    obs = list(sce.objects)
    obs.sort(key=importance_key, reverse=True)

    you = sce.objects['You']
    hitob, _, _ = you.rayCast(
        you.worldPosition - mathutils.Vector((0, 0, 100)),
        you.worldPosition,
        100)

    if hitob is not None:
        print('{sub} are standing on a {ob}'.format(sub=you.name, ob=hitob.name))

    for ob in sce.objects:
        if ob is you:
            continue
        print('There is a {ob}'.format(ob=ob.name))
