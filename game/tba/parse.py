
def _strip(text_split):
    return [
        w for w in text_split
        if w not in {"in", "at", "an"}]

def parse_object(text):
    """ Given some text, return an object. """
    pass

def _parse_command__verb_object(text):
    """ General action on object """
    text_split = text.lower().split()
    text_split = _strip(text_split[1:])
    text_remainder = " ".join(text_split)
    subject = parse_object(" ".join(text_split))
    if subject is None:
        return "{name} can't be found".format(name=text_remainder)
    else:
        return fn(subject)

def parse_command(text):
    """ Parse input, call action (or inspect), and return output """

    # relates to action at the moment

    text_split = text.lower().split()

    # basic action/objects
    if text_split[0] in {"look", "inspect", "check", "investigate"}:
        return _parse_command__verb_object(text, action.inspect_object)

