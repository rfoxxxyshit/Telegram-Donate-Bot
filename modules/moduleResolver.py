from . import tinkoff
print("Preparing module Tinkoff...")
tinkoff = tinkoff.Tinkoff()
print("Tinkoff module loaded.")


class ModuleResolver:
    def __init__(self, using_module: str):
        """Module resolver"""
        self.mod = using_module

    def organizer(self, req: str):
        if self.mod == 'tinkoff':
            return tinkoff.organizer(req)
        else:
            return None

    def description(self, req: str):
        if self.mod == 'tinkoff':
            return tinkoff.description(req)
        else:
            return None

    def name(self, req: str):
        if self.mod == 'tinkoff':
            return tinkoff.name(req)
        else:
            return None

    def target(self, req: str):
        if self.mod == 'tinkoff':
            return tinkoff.target(req)
        else:
            return None

    def collected(self, req: str):
        if self.mod == 'tinkoff':
            return tinkoff.collected(req)
        else:
            return None
