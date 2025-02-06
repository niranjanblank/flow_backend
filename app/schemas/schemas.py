from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


## Board Schemas
class BoardBase(BaseModel):
    """ Base class for other schemas """
    title: str
    description: str
    owner_id: int
    background_image_url: str | None = None


class BoardCreate(BoardBase):
    """ Fields needed when creating a board"""
    background_image_url: str | None = None


class BoardRead(BoardBase):
    """ Fields returned when querying board details"""
    id: int


class BoardUpdate(BoardBase):
    """ Fields that can be updated in a board """
    title: str | None = None
    description: str | None = None
    owner_id: int | None = None
    background_image_url: str | None = None


## User Schemas
class UserBase(BaseModel):
    """ Base class for other schemas """
    username: str
    email: str


class UserCreate(UserBase):
    """ Fields needed when registering user(in this case username, email and password) """
    password: str
    avatar_link: str | None = None
    full_name: str | None = None
    description: str | None = None

class UserRead(UserBase):
    """ Fields returned when querying user details"""
    id: int

class UserUpdate(UserBase):
    """ Fields for updating user"""
    email: str | None = None
    username: str | None = None
    avatar_link: str| None = None
    full_name: str | None = None
    description: str | None = None

## BoardList Schemas
class BoardList(BaseModel):
    """Base class for other list schemas"""
    title: str
    board_id: int
    order: Optional[int] = None


class BoardListCreate(BoardList):
    """Fields needed when creating a board lists"""
    pass


class BoardListRead(BoardList):
    """Fields returned when reading board lists"""
    id: int


class BoardListUpdate(BaseModel):
    title: str | None = None
    order: int | None = None


# Labels Schema
class LabelSchema(BaseModel):
    """Fields of Label"""
    title: str
    color: str
    board_id: int


class LabelRead(LabelSchema):
    id: int


class LabelCreate(LabelSchema):
    pass


class LabelWithBoard(LabelSchema):
    board: BoardRead


class LabelUpdate(LabelSchema):
    title: str | None = None
    color: str | None = None
    board_id: int | None = None


## ListCard Schemas
class ListCardBase(BaseModel):
    """Base class for the cards in a lists"""
    title: str
    desc: str
    list_id: int
    order: Optional[int] = None
    created_at: datetime | None = None
    due_date: datetime | None = None
    updated_at: datetime | None = None
    completed: bool | None = None


class ListCardCreate(ListCardBase):
    """ Attributes required to create a card in a list """
    pass


class ListCardRead(ListCardBase):
    """ Attributes returned when reading list card """
    id: int
    pass


class ListCardUpdate(BaseModel):
    """ Attributes returned when updating list card """
    title: str | None = None
    desc: str | None = None
    list_id: int | None = None
    order: int | None = None
    due_date: datetime | None = None
    completed: bool | None = None


class CardLabelBase(BaseModel):
    label_id: int
    card_id: int


class ListCardWithLabels(ListCardRead):
    labels: list[LabelRead] = []


# for jwt
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    user_id: int


# Relationships
class UserReadWithBoard(UserBase):
    boards: list[BoardRead] = []
    id: int
    avatar_link: str | None = None
    full_name: str | None = None
    description: str | None = None



class BoardReadWithOwner(BoardBase):
    id: int
    owner: UserRead


class BoardListWithCards(BoardListRead):
    list_cards: list[ListCardWithLabels] = []


class BoardReadWithListAndCardAndLabels(BoardRead):
    board_lists: list[BoardListWithCards] = []
    board_labels: list[LabelRead] = []


class ListCardWithList(ListCardRead):
    belongs_to_list: BoardList

class ListWithBoard(BoardListRead):
    board: BoardRead

class CardWithListAndLabel(ListCardWithLabels):
    belongs_to_list: ListWithBoard

# password validator
class PasswordUpdateRequest(BaseModel):
    old_password: str =  Field(..., min_length=4, description="Password must be at least 4 characters long.")
    new_password: str =  Field(..., min_length=4, description="Password must be at least 4 characters long.")