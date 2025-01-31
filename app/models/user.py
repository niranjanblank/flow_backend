from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str
    # this is hashed password
    password: str

    full_name: str | None = None
    description: str | None = None
    avatar_link: str | None = None

    # Relationship to Board
    boards: list["Board"] = Relationship(back_populates="owner")

    # Relationship to Activity
    activities: list["Activity"] = Relationship(back_populates="user")
