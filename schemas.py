from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    isStaff: Optional[bool]
    isActive: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "fazliddin",
                "email": "fazliddinn.gadoyev@gmail.com",
                "password": "1",
                "isStaff": False,
                "isActive": True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = "b876573204cce7bba8ccfa410cedf840999dd42028897f71bb483dc762b9f38a"
    authjwt_access_token_expires: int = 60 * 60 * 60
    authjwt_refresh_token_expires: int = 60 * 60 * 60
    authjwt_algorithm: str = "HS256"


class LoginModel(BaseModel):
    username_or_email: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "fazliddin",
                "password": "1"
            }
        }


class OrderModel(BaseModel):
    quantity: int
    orderStatus: Optional[str] = "PENDING"
    productId: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 7,
                "productId": 1
            }
        }

class OrderUpdateModel(BaseModel):
    quantity: Optional[int]
    productId: Optional[int]


class OrderStatusModel(BaseModel):
    orderStatus: Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "orderStatus": "PENDING"
            }
        }


class ProductModel(BaseModel):
    name: str
    price: float

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "MacBook Pro M1",
                "price": 12321202.0
            }
        }

class ProductEditModel(BaseModel):
    name: Optional[str]
    price: Optional[float]
