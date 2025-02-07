from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()


def test_upload_file_success(
    client: TestClient, db: Session, auth_handler: AuthHandler, test_file
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

    user_email = (
        db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()
    )

    # Generate a JWT token for the user
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Simulate file upload
    response = client.post(
        "/upload/test_folder",
        files={"file": test_file},
        cookies={"access_token": token},
    )

    # Check the response
    assert response.status_code == 200
    assert response.json()["message"] == "File uploaded successfully"


def test_upload_file_folder_not_found(
    client: TestClient, db: Session, auth_handler: AuthHandler, test_file
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

    # Attempt to upload a file to a folder that does not exist
    response = client.post(
        "/upload/non_existent_folder",
        files={"file": test_file},
        cookies={"access_token": token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Folder not found."


def test_upload_file_unauthenticated(client: TestClient, test_file):
    response = client.post("/upload/test_folder", files={"file": test_file})

    assert response.status_code == 401
    assert response.json()["detail"] == "Token not found"
