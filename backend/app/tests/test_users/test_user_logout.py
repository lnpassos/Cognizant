def test_logout(client):
    # Call the logout route
    response = client.post("/logout/")

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}

    # Verify if the access cookie was removed
    assert "access_token" not in response.cookies
