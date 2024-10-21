from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Annotated
from fastapi import Depends
sqlite_file_name = "user.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_user_table():
    SQLModel.metadata.create_all(engine)
    create_test_user()

def get_session():
    with Session(engine) as session:
        yield session

def create_test_user():
    import db.auth
    from db.auth import get_password_hash, User
    hashed_password = get_password_hash("12345678")
    user = User(username="testuser", email="test@example.com", hashed_password=hashed_password)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

SessionDep = Annotated[Session, Depends(get_session)]