from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from database import session, engine
from models import User
from schemas import SignUpModel, LoginModel

session = session(bind=engine)

authRouter = APIRouter(
    prefix="/auth"
)


@authRouter.get("/")
async def welcome(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"message": "Bu auth route signup sahifasi"}


@authRouter.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email bilan oldin user ro'yxatdan o'tgan!"
        )
    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu username bilan odin user ro'yxatdan o'tgan!"
        )
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        isStaff=user.isStaff,
        isActive=user.isActive
    )

    session.add(new_user)
    session.commit()

    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "isStaff": new_user.isStaff,
        "isActive": new_user.isActive
    }
    response = {
        "success": True,
        "code": 201,
        "message": "User is created successfully",
        "data": data
    }

    return response


@authRouter.post("/login", status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(
        or_(User.username == user.username_or_email,
            User.email == user.username_or_email)
    ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        token = {
            "access": access_token,
            "refresh": refresh_token
        }
        response = {
            "success": True,
            "code": 200,
            "message": "User successfully login",
            "data": token
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password yoki username xato!")


@authRouter.get("/login/refresh", status_code=200)
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required() # valid acccess token talab qiladi
        current_user = Authorize.get_jwt_subject() # access tokendan userni ajratib olish

        # Database dan user ni filter qilib olamiz
        db_user = session.query(User).filter(User.username == current_user).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        new_access_token = Authorize.create_access_token(subject=db_user.username)

        response = {
            "success": True,
            "code": 201,
            "message": "New access token is created",
            "data": {
                "access_token": new_access_token
            }
        }
        return response

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
