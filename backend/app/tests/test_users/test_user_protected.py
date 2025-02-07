from app.models.users import User
from app.services.users import get_password_hash


# Test for the protected route
def test_protected_route(client, db, auth_handler):
    # Create a test user in the database
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
    }
    user = User(**user_data)
    db.add(user)
    db.commit()

    # Generate the access token
    access_token = auth_handler.create_access_token(data={"sub": user.email})

    # Simulate an authenticated client with the token stored in the cookie
    client.cookies.set("access_token", access_token)

    # Call the protected route
    response = client.get("/home/")

    assert response.status_code == 200


# Test for the protected route without authentication
def test_protected_route_unauthorized(client):
    response = client.get("/home/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}
