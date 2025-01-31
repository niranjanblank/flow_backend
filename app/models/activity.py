from sqlmodel import SQLModel, Field, Relationship


class Activity(SQLModel, table=True):
    __tablename__ = "activities"
    id: int = Field(default=None, primary_key=True)
    activity_type : str | None = None
    activity_desc: str | None = None
    user_id: int = Field(foreign_key="users.id")

    # Relationship to user
    user:'User' = Relationship(back_populates="activities")

