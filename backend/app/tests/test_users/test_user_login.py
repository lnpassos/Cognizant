from app.models.users import User
from app.services.users import get_password_hash


# Test for the login route
def test_login(client, db):
    # Create a user in the database for testing
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
    }
    user = User(**user_data)
    db.add(user)
    db.commit()

    # Login data
    login_data = {"email": "test@example.com", "password": "testpassword"}

    # Call the login route
    response = client.post("/login/", json=login_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}

    assert "access_token" in response.cookies
