import pytest
from app.models import User  # Adjust import as needed
from app.auth import get_password_hash, verify_password
def test_create_user(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "a-very-secure-password"
    }

    # Send a POST request to the user creation endpoint
    response = client.post("/users/", json=user_data)

    # Assertions to ensure the user was created successfully
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]
    assert "id" in response.json()


def test_get_user_by_id(client, user_data):
    user_id = user_data.id

    # send a get request to retrieve the user
    response = client.get(f"/users/{user_id}")
    print(response.text)
    # assertions to ensure the user is retrieved successfully
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    assert "username" in user  # Ensure the username is present
    assert "email" in user  # Ensure the email is present


def test_user_pagination(client, create_test_users):
    # fetch the data
    response = client.get("/users/?skip=0&limit=5")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 5

    # Test another page of users
    response = client.get("/users/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5  # Expecting the next 5 users

    # Test edge case: Requesting more users than exist
    response = client.get("/users/?skip=0&limit=20")
    assert response.status_code == 200
    data = response.json()
    total_users = len(create_test_users)
    assert len(data) == total_users  # Expecting the total number of users created, as it's less than limit

    # Test edge case: Requesting with high skip
    response = client.get("/users/?skip=15&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # Expecting no users as skip is beyond the total number of users

def test_update_user(client, create_test_user):
    user_id = create_test_user.id  # Get user ID

    updated_data = {
        "email": "updatedemail@example.com",
        "avatar_link": "https://example.com/avatar.jpg",
        "full_name": "Updated Full Name",
        "description": "Updated description"
    }

    # Step 1: Update the user
    response = client.put(f"/users/update/{user_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json() == {"detail": "User updated successfully"}  # ✅ Success message in "detail"

    # Step 2: Fetch the updated user details using GET /users/{user_id}
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200

    updated_user = response.json()

    # Step 3: Verify the updated user details
    assert updated_user["email"] == updated_data["email"]
    assert updated_user["avatar_link"] == updated_data["avatar_link"]
    assert updated_user["full_name"] == updated_data["full_name"]
    assert updated_user["description"] == updated_data["description"]

def test_update_user_partial_data(client, create_test_user):
    user_id = create_test_user.id  # Get an existing user ID

    updated_data = {
        "full_name": "Partially Updated Name"
    }

    # Step 1: Update the user with partial data
    response = client.put(f"/users/update/{user_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json() == {"detail": "User updated successfully"}

    # Step 2: Fetch the updated user details using GET /users/{user_id}
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200

    updated_user = response.json()

    # Step 3: Verify only the provided field is updated
    assert updated_user["full_name"] == updated_data["full_name"]

def test_old_password_incorrect(client, create_test_user):
    """Test if old password is incorrect (400 Bad Request)."""
    response = client.put(
        f"/users/update/password/{create_test_user.id}",
        json={"old_password": "wrongpassword", "new_password": "newpassword"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Old password is incorrect"}


def test_successful_password_update(client, create_test_user, test_db_session):
    """Test if password updates successfully (200 OK)."""
    response = client.put(
        f"/users/update/password/{create_test_user.id}",
        json={"old_password": "securepassword", "new_password": "newpassword"},
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Password updated successfully"}

    # Verify that the password is actually updated in the database
    updated_user = test_db_session.get(User, create_test_user.id)
    assert verify_password("newpassword", updated_user.password) is True


def test_unexpected_error(client, create_test_user, test_db_session, monkeypatch):
    """Test unexpected errors (500 Internal Server Error)."""

    def mock_commit():
        raise Exception("Database commit failed")

    monkeypatch.setattr(test_db_session, "commit", mock_commit)

    response = client.put(
        f"/users/update/password/{create_test_user.id}",
        json={"old_password": "securepassword", "new_password": "newpassword"},
    )

    assert response.status_code == 500
    assert "An error occurred while updating user" in response.json()["detail"]