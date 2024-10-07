from abstract_video_generator import AbstractVideoGenerator
import numpy as np
import moviepy.editor as mpy
import os
from pathlib import Path
class RandomVideoGenerator(AbstractVideoGenerator):
    def generate(self, seed : int, **kwargs) -> str:
        root_path = Path(os.path.join("video_asset", "random"))
        root_path.mkdir(parents=True, exist_ok=True)
        path = str(root_path.joinpath(f"{seed}.mp4"))
        if os.path.exists(path):
            return path
        # Create a function to generate a random frame
        height = kwargs.get("height", 128)
        width = kwargs.get("width", 128)
        fps = kwargs.get("fps", 30)
        duration = kwargs.get("duration", 5)
        # set random seed
        np.random.seed(seed)
        def make_frame(t):
            frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            return frame
        # Create a video clip from the frame-generating function
        clip = mpy.VideoClip(make_frame, duration=duration) 

        # Write the video to a file
        clip.write_videofile(path, fps=fps)
        return path


