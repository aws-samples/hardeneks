from abc import ABC, abstractmethod

from hardeneks import console


class Result(object):
    def __init__(
        self, status=True, resources=[""], resource_type=None, namespace=None
    ):
        self.status = status
        self.resources = resources
        self.resource_type = resource_type
        self.namespace = namespace


class Rule(ABC):

    message = None
    url = None
    _type = None
    pillar = None
    section = None
    console = console

    def __init__(self, result=Result()):
        self.result = result

        if not (hasattr(self, "message") and self.message):
            raise NotImplementedError(
                "Class needs to have class variable message"
            )
        if not (hasattr(self, "url") and self.url):
            raise NotImplementedError("Class needs to have class variable url")
        if not (hasattr(self, "_type") and self._type):
            raise NotImplementedError(
                "Class needs to have class variable _type"
            )
        if not (hasattr(self, "pillar") and self.pillar):
            raise NotImplementedError(
                "Class needs to have class variable pillar"
            )
        if not (hasattr(self, "section") and self.section):
            raise NotImplementedError(
                "Class needs to have class variable section"
            )

    @abstractmethod
    def check(self):
        pass
