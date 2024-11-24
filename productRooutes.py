from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi_jwt_auth import AuthJWT

from database import session, engine
from models import Product, User
from schemas import ProductModel, ProductEditModel

session = session(bind=engine)

productRouter = APIRouter(
    prefix='/product'
)


@productRouter.post("/create", status_code=status.HTTP_201_CREATED)
async def product_create(product: ProductModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.isStaff:
        new_product = Product(
            name=product.name,
            price=product.price
        )
        session.add(new_product)
        session.commit()
        data = {
            "success": True,
            "code": 201,
            "message": "Product is created successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price
            }
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can add new product.")


@productRouter.get("/list", status_code=status.HTTP_200_OK)
async def product_list(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.isStaff:
        products = session.query(Product).all()
        data = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ]
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admin can see all products.")


@productRouter.get("/{id}", status_code=status.HTTP_200_OK)
async def product_detail(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.isStaff:
        product = session.query(Product).filter(Product.id == id).first()
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product topilmadi")
        data = {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admin can see product detail")


@productRouter.delete("/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def product_delete(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.isStaff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            session.delete(product)
            session.commit()

            data = {
                "success": True,
                "code": 204,
                "message": "Product delete is successfully"
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with {id} fot fount")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can deleted")


@productRouter.put("/{id}/edit", status_code=status.HTTP_200_OK)
async def product_edit(id: int, edit_data: ProductEditModel ,Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.isStaff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            for key, value in edit_data.dict(exclude_unset=True).items():
                setattr(product, key, value)
            session.commit()

            data = {
                "success": True,
                "code": 200,
                "message": f"Product with ID {id} has been updated",
                "data": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {id} is not found")












