from ..schemas.schemas import ListCardCreate, ListCardUpdate
from sqlmodel import Session, select
from ..models.board_lists import BoardList
from ..models.list_card import ListCard
from fastapi import HTTPException
from datetime import datetime, date
from sqlalchemy.sql import func, and_


#  Create card in a list
def create_list_card(db: Session, list_card: ListCardCreate):
    """check if the list already exists in the database before adding card to the list"""
    list_exists = db.exec(select(BoardList).where(BoardList.id == list_card.list_id)).first() is not None
    if not list_exists:
        raise HTTPException(status_code=404, detail=f'List with id of {list_card.list_id} doesn\'t exist')
    try:

        # Determine the order
        if list_card.order is None:
            max_order = db.exec(select(ListCard.order).where(ListCard.list_id == list_card.list_id).order_by(
                ListCard.order.desc())).first()
            if max_order is not None:
                new_order = max_order + 1
            else:
                new_order = 1
        else:
            new_order = list_card.order

        db_list_card = ListCard(title=list_card.title,
                                desc=list_card.desc,
                                list_id=list_card.list_id,
                                order=new_order
                                )
        db.add(db_list_card)
        db.commit()
        db.refresh(db_list_card)
        return db_list_card
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred in board creation: {e}")


def read_list_card_by_id(db: Session, list_card_id: int):
    try:
        # Query to find the card
        statement = select(ListCard).where(ListCard.id == list_card_id)
        db_card = db.exec(statement).first()

        if db_card is None:
            raise HTTPException(status_code=404, detail=f"No cards with id {list_card_id}")

        return db_card
    except HTTPException as http_ex:
        # Reraise the HTTPException to be handled by FastAPI
        raise http_ex
    except Exception as e:
        # Handle unexpected errors
        # Log the error or handle it as needed
        raise HTTPException(status_code=500, detail=f"An error occurred while finding the card: {e}")


# read all the card in a list by list_id
def read_list_card_by_list_id(db: Session, list_id: int):
    # check if the list exists
    list_exists = db.exec(select(BoardList).where(BoardList.id == list_id)).first() is not None

    if not list_exists:
        # if list doesnt exists return error
        raise HTTPException(status_code=404, detail=f"List with id of {list_id} not available")

    try:
        statement = select(ListCard).where(ListCard.list_id == list_id)
        list_card_data = db.exec(statement)
        return list_card_data
    except HTTPException as http_ex:
        # Reraise the HTTPException to be handled by FastAPI
        raise http_ex
    except Exception as e:
        # Handle unexpected errors
        # Log the error or handle it as needed
        raise HTTPException(status_code=500, detail=f"An error occurred while getting Board Lists: {e}")


# Find the card in a list with the highest order property
def find_highest_order_card_in_list(db: Session, list_id: int):
    try:
        # Query to find the card with the highest order in the given list_id
        statement = select(ListCard).where(ListCard.list_id == list_id).order_by(ListCard.order.desc())
        highest_order_card = db.exec(statement).first()

        if highest_order_card is None:
            raise HTTPException(status_code=404, detail=f"No cards found in list with id {list_id}")

        return highest_order_card
    except HTTPException as http_ex:
        # Reraise the HTTPException to be handled by FastAPI
        raise http_ex
    except Exception as e:
        # Handle unexpected errors
        # Log the error or handle it as needed
        raise HTTPException(status_code=500, detail=f"An error occurred while finding the highest order card: {e}")


def update_list_card(db: Session, list_card_id: int, card_update: ListCardUpdate):
    """
    Update the list card based on the data given
    """
    try:
        db_card = db.get(ListCard, list_card_id)
        if not db_card:
            raise HTTPException(status_code=404, detail="Card not found")
        # exclude_unset excludes any fields that have not been assigned a value
        update_data = card_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_card, key, value)

        # Update the updated_at field
        db_card.updated_at = datetime.utcnow()

        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return db_card
    except HTTPException as http_ex:
        # Reraise the HTTPException to be handled by FastAPI
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred in card: {e}")


def delete_card_by_id(db: Session, list_card_id):
    """ Delete card list by id"""
    try:
        db_card = db.get(ListCard, list_card_id)
        if not db_card:
            raise HTTPException(status_code=404, detail="Card not found")
        db.delete(db_card)
        db.commit()
        return {"deleted": True}
    except HTTPException as http_ex:
        # Reraise the HTTPException to be handled by FastAPI
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred in card deletion: {e}")


def read_cards_due_today(db: Session):
    """Fetch all cards that are due today"""
    try:
        current_date = date.today()
        statement = select(ListCard).where(func.date(ListCard.due_date) == current_date)
        cards_due_today = db.exec(statement).all()

        return cards_due_today
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching today's cards: {e}")

def read_cards_overdue_today(db: Session):
    """ Fetch all cards that are overdue today"""
    try:
        current_date = date.today()
        statement = select(ListCard).where(and_(func.date(ListCard.due_date) < current_date, ~ListCard.completed))
        cards_overdue = db.exec(statement).all()
        return cards_overdue

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching today's cards: {e}")

def read_cards_upcoming(db: Session):
    """ Fetch all cards that are upcoming """
    try:
        current_date = date.today()
        statement = select(ListCard).where(and_(func.date(ListCard.due_date) > current_date, ~ListCard.completed))

        cards_upcoming= db.exec(statement).all()
        return cards_upcoming

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching upcoming cards: {e}")

