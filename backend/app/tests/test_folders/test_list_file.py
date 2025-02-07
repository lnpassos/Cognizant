from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler


def test_get_files_in_folder_success(
    client: TestClient, db: Session, auth_handler: AuthHandler
):
    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Create a test folder
    test_folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(test_folder)
    db.commit()

    # Create files in the test folder
    file_data = [
        {"filename": "file1.txt", "file_path": "/test_folder/file1.txt"},
        {"filename": "file2.txt", "file_path": "/test_folder/file2.txt"},
    ]
    for file in file_data:
        new_file = foldersModels.File(
            filename=file["filename"],
            file_path=file["file_path"],
            folder_id=test_folder.id,
            user_id=user.id,
        )
        db.add(new_file)
    db.commit()

    user_email = (
        db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()
    )

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Simulate the request to list files in the folder
    response = client.get(
        "/folders/test_folder/files/", cookies={"access_token": token}
    )

    # Check the response
    assert response.status_code == 200
    files = response.json()
    assert len(files) == 2
    assert files[0]["filename"] == "file1.txt"
    assert files[1]["filename"] == "file2.txt"


def test_get_files_in_folder_not_found(
    client: TestClient, db: Session, auth_handler: AuthHandler
):
    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    user_email = (
        db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()
    )

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Try to list files from a non-existent folder
    response = client.get(
        "/folders/non_existent_folder/files/", cookies={"access_token": token}
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"] == "You don't have permission to access this folder."
    )


def test_get_files_in_folder_unauthenticated(client: TestClient):
    response = client.get("/folders/test_folder/files/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token not found"
