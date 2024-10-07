from abc import ABC, abstractmethod
from typing import *
class AbstractVideoGenerator(ABC):
    # generate a video given a seed and video type
    # return the path to the video
    @abstractmethod
    def generate(self, seed : int, **kwargs) -> str:
        pass

class VideoGeneratorRouter:
    def __init__(self) -> None:
        self.routers : Dict[str, AbstractVideoGenerator] = {}
    def register(self, typ : str, generator : AbstractVideoGenerator):
        self.routers[typ] = generator
    def generate(self, typ : str, seed : int, **kwargs) -> str:
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return self.routers[typ].generate(seed, **kwargs)