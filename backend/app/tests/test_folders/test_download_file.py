import os
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()
UPLOAD_FOLDER = "uploads"


def test_download_file_authenticated(client, db):
    # Create a user for the test
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Create a folder for the user
    folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(folder)
    db.commit()

    # Add a sample file to the folder
    folder_full_path = os.path.join(UPLOAD_FOLDER, user.email, "test_folder")
    os.makedirs(folder_full_path, exist_ok=True)
    file_path = os.path.join(folder_full_path, "testfile.txt")
    with open(file_path, "w") as f:
        f.write("Test file content")

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Set the "access_token" cookie on the client
    client.cookies.set("access_token", token)

    # Make a GET request to the file download route
    response = client.get(
        "/download/test_folder/testfile.txt", cookies={"access_token": token}
    )

    assert response.status_code == 200

    # Check the MIME type of the response
    content_type = response.headers["Content-Type"].split(";")[0]
    assert content_type == "text/plain"

    # Check if the content of the file is as expected (decoding bytes to string)
    assert response.content.decode("utf-8") == "Test file content"

    # Cleanup: Remove the created file and folder after the test
    os.remove(file_path)
    os.rmdir(folder_full_path)
    db.delete(folder)
    db.commit()


def test_download_file_not_found(client, db):
    # Create a user for the test
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Create the folder in the database to avoid "Folder not found" error
    folder_data = {"path": "test_folder", "user_id": user.id}
    folder = foldersModels.Folder(**folder_data)
    db.add(folder)
    db.commit()

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Set the "access_token" cookie on the client
    client.cookies.set("access_token", token)

    # Try to access a file that doesn't exist within the existing folder
    response = client.get(
        "/download/test_folder/nonexistentfile.txt", cookies={"access_token": token}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found."}
