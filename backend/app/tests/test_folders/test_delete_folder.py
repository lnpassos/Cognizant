import os
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()


def test_delete_folder_success(client, db, auth_handler):
    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Create a test folder for the user
    test_folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(test_folder)
    db.commit()

    # Create a test file in the folder
    test_file = foldersModels.File(
        filename="test_file.txt",
        file_path=os.path.join("uploads", user.email, "test_folder", "test_file.txt"),
        user_id=user.id,
        folder_id=test_folder.id,
    )
    db.add(test_file)
    db.commit()

    # Create the folder and file in the file system
    folder_full_path = os.path.join("uploads", user.email, "test_folder")
    os.makedirs(folder_full_path, exist_ok=True)
    with open(os.path.join(folder_full_path, "test_file.txt"), "w") as f:
        f.write("Test file content")

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Send the request to delete the folder
    response = client.delete(
        "/delete_folder/test_folder", cookies={"access_token": token}
    )

    # Verify the response
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Folder 'test_folder' and its files were successfully deleted!"
    )

    # Check if the folder was removed from the database
    deleted_folder = (
        db.query(foldersModels.Folder)
        .filter(foldersModels.Folder.id == test_folder.id)
        .first()
    )
    assert deleted_folder is None

    # Check if the file was removed from the database
    deleted_file = (
        db.query(foldersModels.File)
        .filter(foldersModels.File.id == test_file.id)
        .first()
    )
    assert deleted_file is None

    # Check if the folder was removed from the file system
    assert not os.path.exists(folder_full_path)


def test_delete_folder_not_found(client, db, auth_handler):
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

    # Send the request to delete a non-existent folder
    response = client.delete(
        "/delete_folder/nonexistent_folder", cookies={"access_token": token}
    )

    # Verify the response
    assert response.status_code == 404
    assert response.json()["detail"] == "Folder not found."
