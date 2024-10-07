from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from typing import Optional

# Import your video generation function
from abstract_video_generator import AbstractVideoGenerator, VideoGeneratorRouter
from random_video_generator import RandomVideoGenerator

video_generator_router = VideoGeneratorRouter()
video_generator_router.register("random", RandomVideoGenerator())
app = FastAPI()
origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/video-generate/{type}/{seed}")
async def generate_video(type : str, 
                         seed : int,
                         height : Optional[int] = None,
                         width : Optional[int] = None,
                         fps : Optional[int] = None,
                         duration : Optional[int] = None):
    try:
        # Return the video file as a response
        path = video_generator_router.generate(type, seed, height=height, width=width, fps=fps, duration=duration)
        return FileResponse(path, media_type="audio/mpeg")

    except Exception as e:
        # If an error occurs, raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)