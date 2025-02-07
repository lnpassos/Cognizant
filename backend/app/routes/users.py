from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import users as schemas
from app.services.users import register_user, get_user_by_email, verify_password
from app.auth.jwt import AuthHandler
from fastapi import Request


router = APIRouter()

# Instance of AuthHandler
auth_handler = AuthHandler()


# Register user
@router.post("/register/")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    register_user(user, db)
    return JSONResponse({"message": "User successfully created"})


# Login
@router.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Find user in database
    db_user = get_user_by_email(db, email=user.email)

    # Verifying data
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Generate token
    access_token = auth_handler.create_access_token(data={"sub": db_user.email})

    # Creating a token cookie with safe parameters
    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="Strict",
        secure=True,
        max_age=30 * 60,  # 30 minutes
    )

    return response


# Home protected
@router.get("/home/")
def protected_route(request: Request, db: Session = Depends(get_db)):
    try:
        email = auth_handler.get_current_user(request)  # Get user email from token
        db_user = get_user_by_email(db, email=email)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": f"Welcome, {db_user.username}!"}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# Logout
@router.post("/logout/")
def logout():
    response = JSONResponse({"message": "Logout successful"})
    # Removing the token cookie
    response.delete_cookie("access_token", path="/", domain=None)

    return response
