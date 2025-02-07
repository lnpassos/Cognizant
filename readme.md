# API Documentation

## Project Overview

This project is a **document and folder management system** based on URLs. It allows users to create dynamic URLs to store and manage files securely. Only the user who created a file or folder can access and manage them, ensuring privacy through **JWT authentication** and robust security validations.

### Example:
A folder such as `documents/reviews` can store multiple files that can be accessed and managed at any time. When uploading a file with the same name, the system automatically assigns a version number to maintain a **file versioning system**.

For instance:
```
review.pdf
review_v1.pdf
review_v2.pdf
```
This ensures previous versions of a file are retained and accessible.

---

## Project Setup and Initialization

### Prerequisites
Ensure you have the following installed on your machine:

- **Python 3.8+**
- **Node.js (Latest LTS Version)**
- **pip (Python Package Manager)**
- **npm (Node Package Manager)**

## Step-by-Step Guide

### 1. Start the Backend Server

1. Open a terminal and navigate to the backend directory:
   
   ```sh
   cd backend
   ```

2. Install the required dependencies:
   
   ```sh
   pip install -r requirements.txt
   ```

3. Start the backend server using Uvicorn:
   
   ```sh
   uvicorn app.main:app --reload
   ```

### 2. Start the Frontend Server

1. Open a new terminal and navigate to the frontend directory:
   
   ```sh
   cd frontend
   ```

2. Install the required dependencies:
   
   ```sh
   npm install
   ```

3. Start the frontend development server:
   
   ```sh
   npm run dev
   ```

### 3. Access the Application

Once both the backend and frontend are running, open your browser and navigate to:

👉 [http://localhost:3000/](http://localhost:3000/)

### Important Notes

- Both the **backend** and **frontend** must be running simultaneously for the system to function properly.
- If you encounter any errors, ensure all dependencies are correctly installed and that the ports are not in use.

**Recommendation**: When you start the project, click on *Virtual Assistant* in the bottom-right corner and select option *? Need Help*. Our AI is ready to assist you with the first steps.



## Authentication Endpoints

### Register User
**POST** `/register/`
- **Description**: Creates a new user account.
- **Request Body**:
  - `username`: string (User's name)
  - `email`: string (User's email address)
  - `password`: string (User's password)
- **Response**:
  - `message`: "User successfully created"

### Login
**POST** `/login/`
- **Description**: Authenticates a user and returns an authentication token.
- **Request Body**:
  - `email`: string (User's email address)
  - `password`: string (User's password)
- **Response**:
  - `message`: "Login successful"
  - Sets an `access_token` cookie with a 30-minute expiration time.

### Protected Home Route
**GET** `/home/`
- **Description**: A protected route for you to manage your system.
- **Request Headers**:
  - `Cookie`: access_token (JWT authentication token)
- **Response**:
  - `message`: "Welcome, {username}!"

### Logout
**POST** `/logout/`
- **Description**: Logs out a user by deleting the authentication cookie.
- **Response**:
  - `message`: "Logout successful"

---

## Folder Management Endpoints

### Create a Folder
**POST** `/create_folder/`
- **Description**: Creates a new folder for the authenticated user.
- **Request Body**:
  - `folder_path`: string (Path of the folder to be created)
  - `files`: List of `UploadFile` (Optional files to be uploaded within the folder)
- **Response**:
  - Returns folder details or an error message if unauthorized.

### List User Folders
**GET** `/folders/`
- **Description**: Retrieves all folders associated with the authenticated user.
- **Response**:
  - A list of folders.

### Upload a File
**POST** `/upload/{folder_name:path}`
- **Description**: Uploads a file to a specified folder.
- **Path Parameters**:
  - `folder_name`: string (Folder path where the file will be uploaded)
- **Request Body**:
  - `file`: `UploadFile` (File to be uploaded)
- **Response**:
  - Upload confirmation or an error message.

### List Files in a Folder
**GET** `/folders/{folder_path:path}/files/`
- **Description**: Retrieves all files inside a specified folder.
- **Path Parameters**:
  - `folder_path`: string (Path of the folder)
- **Response**:
  - A list of files within the specified folder.

### Delete a Folder
**DELETE** `/delete_folder/{folder_path:path}`
- **Description**: Deletes a folder and all its contents.
- **Path Parameters**:
  - `folder_path`: string (Folder path to be deleted)
- **Response**:
  - Success message or an error.

### Delete a File
**DELETE** `/delete_file/{folder_path:path}/{filename}`
- **Description**: Deletes a specific file from a folder.
- **Path Parameters**:
  - `folder_path`: string (Path of the folder containing the file)
  - `filename`: string (Name of the file to be deleted)
- **Response**:
  - Success message or an error.

### Download a File
**GET** `/download/{folder_path:path}/{filename}`
- **Description**: Downloads a specified file.
- **Path Parameters**:
  - `folder_path`: string (Path of the folder containing the file)
  - `filename`: string (Name of the file to be downloaded)
- **Response**:
  - The requested file.

### Preview a File
**GET** `/folders/{folder_path:path}/{filename}`
- **Description**: Provides a preview of a file if compatible with browser rendering.
- **Path Parameters**:
  - `folder_path`: string (Path of the folder containing the file)
  - `filename`: string (Name of the file to preview)
- **Query Parameters**:
  - `review`: int (Optional file revision number)
- **Response**:
  - A file preview or an error if unsupported.

---

# Unit Tests

To test the project using unit tests, you need to be inside the `backend` folder. Use the following command:

```sh
cd backend
```

You can run the tests individually or all at once. Below are the commands to execute the tests:

## Running Tests

### Folder and File Tests  
To test folders and files, run the following command:
**Windows Powershell**
```sh
$env:PYTHONPATH = "./"; pytest app/tests/test_folders
```

**Ubuntu/Linux(or WSL)**
```sh
PYTHONPATH=./ pytest app/tests/test_folders
```

### User Tests  
To test user-related functionality, run the following command:

**Windows Powershell**
```sh
$env:PYTHONPATH = "./"; pytest app/tests/test_users
```

**Ubuntu/Linux(or WSL)**
```sh
PYTHONPATH=./ pytest app/tests/test_users
```

### Running All Tests  
To run all tests at once, use the following command:

**Windows Powershell**
```sh
$env:PYTHONPATH = "./"; pytest app/tests
```

**Ubuntu/Linux(or WSL)**
```sh
PYTHONPATH=./ pytest app/tests
```

## Notes  

- **Individual Tests**: You can run specific test files or test functions by specifying the path. Example:

**Windows Powershell**  
  ```sh
 $env:PYTHONPATH = "./"; pytest app/tests/test_folders/test_create_folder.py::test_create_folder
  ```  

**Ubuntu/Linux(or WSL)**
```sh
PYTHONPATH=./ pytest app/tests/test_folders/test_create_folder.py::test_create_folder
```
  
- **Test Coverage**: Ensure you have the necessary dependencies installed to measure test coverage if required.  
- **Environment Variables**: The `PYTHONPATH=./` ensures that Python can locate the project modules correctly during testing.  


## Chatbot API
The system also includes an **AI-powered chatbot** that offers two functionalities:
1. **Help Mode (`help`)**: Guides users on how to utilize the system effectively.
2. **Free Mode (`free`)**: Provides open-ended AI-powered conversations via the ChatGPT API.

### Chatbot Endpoint
**POST** `/chatbot`
- **Description**: Handles chatbot interactions based on the selected mode.
- **Request Body**:
  - `message`: string (User's message)
  - `chatMode`: string (`help` or `free`)
- **Response**:
  - AI-generated reply.


## Conclusion
This API provides a **secure and efficient** document and folder management system with advanced file versioning and authentication controls. Additionally, the built-in AI-powered chatbot enhances user experience by offering real-time assistance and open-ended conversations. Future updates may introduce **advanced permissions, collaborative file management, and deeper AI integrations** to further optimize user productivity and security.

