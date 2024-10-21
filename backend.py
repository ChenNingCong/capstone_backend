from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from typing import Optional, Annotated
from fastapi import Depends
from db.init import create_user_table
from db.auth import router as auth_router, get_current_user, User
from db.model.user_requested_video import make_new_request, get_latest_user_requested_video, UserRequestedVideo
from db.init import SessionDep
# Import your video generation function
from abstract_video_generator import AbstractVideoGenerator, VideoGeneratorRouter
from random_video_generator import RandomVideoGenerator

video_generator_router = VideoGeneratorRouter()
video_generator_router.register("random", RandomVideoGenerator())
app = FastAPI()
origins = [
    "http://localhost:5173"
]
app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/video-generate/{type}/{seed}")
async def generate_video(current_user: Annotated[User, Depends(get_current_user)],
                         session : SessionDep,
                         typ : str, 
                         seed : int,
                         height : Optional[int] = None,
                         width : Optional[int] = None,
                         fps : Optional[int] = None,
                         duration : Optional[int] = None):
    try:
        # Return the video file as a response
        kwargs = video_generator_router.default_kwargs(typ, height=height, width=width, fps=fps, duration=duration)
        user_id = current_user.id
        request = make_new_request(session, user_id=user_id,**kwargs)
        if request is None:
            raise HTTPException(status_code=400, detail="The user already has one video in generation.")
        return request
        #path = video_generator_router.generate(typ = typ, seed=request.id, **kwargs)
        #return FileResponse(path, media_type="audio/mpeg")

    except Exception as e:
        # If an error occurs, raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))

import os
@app.on_event("startup")
def on_startup():
    if os.path.exists("user.db"):
        os.remove("user.db")
    create_user_table()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)