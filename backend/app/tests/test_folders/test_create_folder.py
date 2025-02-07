import os
from app.models import users as usersModels, folders as foldersModels
from app.services.users import get_password_hash
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()


def test_create_folder(client, db):
    # Create a test user in the database
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Generate the JWT token for the user using create_access_token
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Set the "access_token" cookie in the client
    client.cookies.set("access_token", token)

    folder_data = {
        "folder_path": "new_folder",
    }

    # Call the folder creation route
    response = client.post("/create_folder/", data=folder_data)

    # Check if the response was successful
    assert response.status_code == 200
    assert response.json() == {"message": "Folder created successfully!"}

    # Verify if the folder was created in the database
    folder = (
        db.query(foldersModels.Folder)
        .filter(foldersModels.Folder.path == "new_folder")
        .first()
    )
    assert folder is not None
    assert folder.path == "new_folder"
    assert folder.user_id == user.id

    # Verify if the folder was created in the uploads directory
    user_folder_path = os.path.join("uploads", user.email, "new_folder")
    assert os.path.exists(user_folder_path)

    os.rmdir(user_folder_path)
