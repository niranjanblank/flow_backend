import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlmodel import create_engine, Session, SQLModel
from app.database import get_session
import os
from dotenv import load_dotenv
from ..models.user import User
from ..models.board import Board
from ..models.board_lists import BoardList
from ..models.list_card import ListCard
from ..models.board_label import BoardLabel
from ..models.card_label import CardLabelLink
from app.auth import get_password_hash
load_dotenv()

TEST_DB_URL = os.getenv('TEST_DB_URL')


@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine(TEST_DB_URL)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session  # use this session
        session.flush()  # Ensure all changes are flushed to the database
        session.expire_all()  # Expire all instances in the session to clear any cached state
    except Exception as e:
        transaction.rollback()  # Rollback the transaction on any exception
        raise e
    finally:
        session.close()  # Close the session
        if transaction.is_active:
            transaction.rollback()  # Rollback the transaction if it's still active
        connection.close()  # Close the connection


@pytest.fixture(scope="function")
def client(test_db_session):
    # Dependency override for the database session
    app.dependency_overrides[get_session] = lambda: test_db_session
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def user_data(test_db_session):
    # Insert test user data here
    new_user = User(username="testuser", email="test@example.com", password="hashedpassword")
    test_db_session.add(new_user)
    test_db_session.commit()
    test_db_session.refresh(new_user)
    return new_user  # return the user object or just the user ID as needed


@pytest.fixture(scope="function")
def board_data(test_db_session: Session, user_data: User):
    # Create a test board with owner_id from user_data

    test_board = Board(title="Test Board", description="This is a test board", owner_id=user_data.id)
    test_db_session.add(test_board)
    test_db_session.commit()
    test_db_session.refresh(test_board)  # Refresh to load any additional attributes
    return test_board

@pytest.fixture(scope="function")
def board_list_data_single(test_db_session: Session, board_data: Board):
    # Create a test board list with board_id from board_data

    test_board_list = BoardList(board_id=board_data.id, title="List 1", description="Description for list 1",order=1)
    test_db_session.add(test_board_list)
    test_db_session.commit()
    test_db_session.refresh(test_board_list)  # Refresh to load any additional attributes
    return test_board_list

# Fixture to create users in the database
@pytest.fixture(scope="function")
def create_test_users(test_db_session: Session, ):
    users = [
        User(username=f"user{i}", email=f"user{i}@example.com", password="testpassword")
        for i in range(10)  # Adjust the range for desired number of test users
    ]
    test_db_session.add_all(users)
    test_db_session.commit()
    return users


@pytest.fixture(scope="function")
def create_test_user(test_db_session):
    """Fixture to create a test user in the database with minimal fields"""
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        password=get_password_hash("securepassword"),  # Hash the password
        full_name="Test User",
        description=None,  # Set to None
        avatar_link=None  # Set to None
    )

    test_db_session.add(test_user)
    test_db_session.commit()
    test_db_session.refresh(test_user)

    return test_user  # Return the created user object

# Fixture to create boards in the database
@pytest.fixture(scope="function")
def create_test_boards(test_db_session, create_test_users):
    boards = [
        Board(title=f"Board {i}", description=f"Description {i}",
              owner_id=create_test_users[i % len(create_test_users)].id)
        for i in range(20)  # Creating 20 test boards
    ]
    test_db_session.add_all(boards)
    test_db_session.commit()
    return boards

@pytest.fixture(scope="function")
def create_board_data_single_owner(test_db_session, user_data):
    boards = [
        Board(title=f"Board {i}", description=f"Description {i}",
              owner_id=user_data.id)
        for i in range(20)  # Creating 20 test boards
    ]
    test_db_session.add_all(boards)
    test_db_session.commit()
    return boards

# Fixture to add lists to the board
@pytest.fixture(scope="function")
def board_list_data(test_db_session, board_data):
    test_board_lists = [
        BoardList(board_id=board_data.id, title="List 1", description="Description for list 1", order=0),
        BoardList(board_id=board_data.id, title="List 2", description="Description for list 2", order=1),
    ]

    for board_list in test_board_lists:
        test_db_session.add(board_list)
    test_db_session.commit()

    return test_board_lists

# Fixture to add cards to a list
@pytest.fixture(scope="function")
def list_card_data(test_db_session, board_list_data):
    # add multiple cards to list
    list_cards = [
        ListCard(title="Card 1", desc="Description for card 1", list_id=board_list_data[0].id, order=0),
        ListCard(title="Card 2", desc="Description for card 2", list_id=board_list_data[0].id, order=1),
        ListCard(title="Card 3", desc="Description for card 3", list_id=board_list_data[0].id, order=2),
    ]

    for list_card in list_cards:
        test_db_session.add(list_card)
    test_db_session.commit()

    return list_cards

#fixture for singe label
@pytest.fixture(scope="function")
def label_data(test_db_session, board_data):
    test_label = BoardLabel(title="Label 1", color="#FF5733", board_id=board_data.id)
    test_db_session.add(test_label)
    test_db_session.commit()
    test_db_session.refresh(test_label)
    return test_label

# fixture for labels data
@pytest.fixture(scope="function")
def labels_data(test_db_session, board_data):
    # adding labels
    test_labels = [
        BoardLabel(title="Label 1", color="#FF5733", board_id=board_data.id),
        BoardLabel(title="Label 2", color="#33FF57", board_id=board_data.id),
        BoardLabel(title="Label 3", color="#3357FF", board_id=board_data.id)
    ]

    for label in test_labels:
        test_db_session.add(label)
    test_db_session.commit()

    return test_labels

@pytest.fixture(scope="function")
def card_label_data(test_db_session: Session, list_card_data, label_data):
    # This fixture creates a CardLabelLink instance for testing
    card_label = CardLabelLink(card_id=list_card_data[0].id, label_id=label_data.id)
    test_db_session.add(card_label)
    test_db_session.commit()
    test_db_session.refresh(card_label)
    return card_label