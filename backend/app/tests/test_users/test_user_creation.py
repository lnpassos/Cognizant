from app.models.users import User


# Test for the registration route
def test_register(client, db):
    # Test data
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }

    # Call the registration route
    response = client.post("/register/", json=user_data)

    assert response.status_code == 200
    assert response.json() == {"message": "User successfully created"}

    # Verify that the user was created in the database
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.username == user_data["username"]
