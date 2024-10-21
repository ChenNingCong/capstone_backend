from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from typing import Optional, Annotated
from fastapi import Depends

# Import your video generation function
from generator.abstract_video_generator import video_generator_router
from db.model.user_requested_video import make_new_request, get_latest_user_requested_video, UserRequestedVideo, update_status
from db.auth import router as get_current_user, User
from db.init import SessionDep
# we must import auth_router here because the dependency on Scope (required by annotation)
from db.auth import router as auth_router, get_current_user, User

app = FastAPI()
origins = [
    "http://localhost:8080"
]

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
                         type : str, 
                         seed : int,
                         height : Optional[int] = None,
                         width : Optional[int] = None,
                         fps : Optional[int] = None,
                         duration : Optional[int] = None):
    try:
        # Return the video file as a response
        kwargs = video_generator_router.default_kwargs(type, height=height, width=width, fps=fps, duration=duration)
        user_id = current_user.id
        request = make_new_request(session, user_id=user_id, seed = seed, type=type, **kwargs)
        if request is None:
            raise HTTPException(status_code=400, detail="The user already has one video in generation.")
        #return request
        path = video_generator_router.generate(typ = type, resource_id=request.id, **kwargs)
        update_status(session, request.id)
        return {"path" : path}

    except Exception as e:
        # If an error occurs, raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))

import os
import shutil
import argparse
import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="0.0.0.0")   
    parser.add_argument('--port', type=int, default=8080)   
    args = parser.parse_args()
    print(args)
    uvicorn.run(app, host=args.host, port=args.port)