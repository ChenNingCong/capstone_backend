from sqlmodel import Field, SQLModel, Session, select
from typing import Optional
import datetime

class UserRequestedVideo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type : str
    seed : int
    height: int
    width: int
    fps: int
    duration: int

    requested_time: int
    finished: bool


# user verification
def get_latest_user_requested_video(session: Session, user_id: int):
    # timezone is unreliable, use id here...
    statement = (
        select(UserRequestedVideo)
        .where(UserRequestedVideo.user_id == user_id)
        .order_by(UserRequestedVideo.id.desc())
        .limit(1)
    )
    result = session.exec(statement)
    return result.first()


def is_all_finished(session: Session, user_id: int):
    item = get_latest_user_requested_video(session, user_id)
    return item is None or item.finished


def make_new_request(
    session: Session, user_id: int, type :str,  seed : int, height: int, width: int, fps: int, duration: int
) -> Optional[UserRequestedVideo]:
    if is_all_finished(session, user_id):
        request = UserRequestedVideo(
            user_id=user_id,
            type=type,
            seed=seed,
            height=height,
            width=width,
            fps=fps, duration=duration, requested_time=datetime.datetime.utcnow(), finished=False)
        session.add(request)
        session.commit()
        session.refresh(request)
        return request
    else:
        return None

def update_field(session, model, id, field_name, new_value):
    # Query the record by id
    statement = select(model).where(model.id == id)
    result = session.exec(statement).first()
    
    if result:
        # Update the field
        setattr(result, field_name, new_value)
        session.add(result)
        session.commit()
        session.refresh(result)
        return result
    else:
        return None

def update_status(session, id):
    return update_field(session, UserRequestedVideo, id, "finished", True)