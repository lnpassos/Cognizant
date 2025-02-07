from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()


def test_list_folders(client, db, auth_handler):
    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Create some folders associated with the user
    folder1 = foldersModels.Folder(path="folder1", user_id=user.id)
    folder2 = foldersModels.Folder(path="folder2", user_id=user.id)
    db.add(folder1)
    db.add(folder2)
    db.commit()

    # Call the route to list folders, including the token in the authentication cookie
    response = client.get("/folders/", cookies={"access_token": token})

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert any(folder["path"] == "folder1" for folder in response_json)
    assert any(folder["path"] == "folder2" for folder in response_json)
