from sqlmodel import Field, SQLModel, Session, select
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username : str
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(index=True)

# user verification
def get_user(session : Session, email : str) -> Optional[User]:  
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    return result.first()

