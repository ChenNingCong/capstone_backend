from abc import ABC, abstractmethod
from typing import *
class AbstractVideoGenerator(ABC):
    # generate a video given a seed and video type
    # return the path to the video
    @abstractmethod
    def generate(self, seed : int, **kwargs) -> str:
        pass
    @abstractmethod
    def default_kwargs(self, **kwargs):
        pass

class VideoGeneratorRouter:
    def __init__(self) -> None:
        self.routers : Dict[str, AbstractVideoGenerator] = {}
    def register(self, typ : str, generator : AbstractVideoGenerator):
        self.routers[typ] = generator
    def generate(self, typ : str, seed : int, **kwargs) -> str:
        return self.routers[typ].generate(seed, **kwargs)
    def default_kwargs(self, typ : str, **kwargs):
        return self.routers[typ].default_kwargs(**kwargs)
