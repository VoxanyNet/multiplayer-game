class Unresolved:
    # represents an attribute that needs to be resolved from its uuid to its actual object
    def __init__(self, uuid):
        # the object's uuid that we need to resolve to an actual object
        self.uuid = uuid
