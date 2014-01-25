import bge

def _strip(text_split):
    return [
        w for w in text_split
        if w not in {"in", "at", "an"}]


def parse_node(p, text):
    """ Given some text, return an object. """
    scene = bge.logic.getCurrentScene()
    node = p.get_node(text)
    return node


def _parse_command__verb_object(n, p, text, fn):
    """ General action on object """
    text_split = text.lower().split()
    text_split = _strip(text_split[1:])
    text_remainder = " ".join(text_split)
    node_subject = parse_node(p, " ".join(text_split))
    if node_subject is None:
        return "{name} can't be found".format(name=text_remainder)
    else:
        return fn(n, p, node_subject)


def parse_command(n, p, text):
    """ Parse input, call action (or inspect), and return output """

    # relates to action at the moment
    from . import action

    text_split = text.lower().split()

    # basic action/objects
    if text_split[0] in {"look", "inspect", "check", "investigate"}:
        return _parse_command__verb_object(n, p, text, action.inspect_node)

    return "Not sure what you mean"

