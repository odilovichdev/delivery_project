from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT

from database import session, engine
from models import User, Order, Product
from schemas import OrderModel, OrderUpdateModel, OrderStatusModel

session = session(bind=engine)

orderRouter = APIRouter(
    prefix="/order"
)


@orderRouter.get("/")
async def welcome_page(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    return {
        "message": "Bu order route sahifasi"
    }


@orderRouter.post("/make", status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    curren_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == curren_user).first()
    new_order = Order(
        quantity=order.quantity,
        productId=order.productId
    )
    product = session.query(Product).filter(Product.id == order.productId).first()
    new_order.totalprice = new_order.quantity * product.price
    new_order.user = user  # ToDo
    session.add(new_order)
    session.commit()

    response = {
        "success": True,
        "code": 201,
        "message": "Order is created is successfully",
        "data": {
            "id": new_order.id,
            "product": {
                "id": new_order.product.id,
                "name": new_order.product.name,
                "price": new_order.product.price
            },
            "quantity": new_order.quantity,
            "totalprice": new_order.totalprice,
            "orderStatus": new_order.orderStatus.value
        }
    }
    return jsonable_encoder(response)


@orderRouter.get("/list", status_code=status.HTTP_200_OK)
async def orders_list(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.isStaff:
        orders = session.query(Order).all()
        data = [
            {
                "id": order.id,
                "quantity": order.quantity,
                "totalprice": order.totalprice,
                "orderStatus": order.orderStatus.value,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                }
            }
            for order in orders
        ]
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Super Admin can see all orders")


@orderRouter.get("/{id}", status_code=status.HTTP_200_OK)
async def order_detail(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.isStaff:
        order = session.query(Order).filter(Order.id == id).first()

        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order topilmadi")
        data = {
            "id": order.id,
            "quantity": order.quantity,
            "totalprice": order.totalprice,
            "orderStatus": order.orderStatus.value,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            }
        }
        return jsonable_encoder(data)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Super Admin is allowed to this request")


@orderRouter.get("/user/orders", status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    data = [
        {
            "id": order.id,
            "quantity": order.quantity,
            "totalprice": order.totalprice,
            "orderStatus": order.orderStatus.value,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            }
        }
        for order in user.orders
    ]
    return jsonable_encoder(data)


@orderRouter.get("/user/order/{id}", status_code=status.HTTP_200_OK)
async def get_user_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order = session.query(Order).filter(Order.id == id, Order.user == user).first()

    if order:
        data = {
            "id": order.id,
            "quantity": order.quantity,
            "totalprice": order.totalprice,
            "orderStatus": order.orderStatus.value,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            }
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} li ma'lumot topilmadi!")


@orderRouter.put("/{id}/edit", status_code=status.HTTP_200_OK)
async def order_edit(id: int, edit_order: OrderUpdateModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    order = session.query(Order).filter(Order.id == id).first()

    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Siz boshqa userlarni orderlarini tahrirlay olmaysiz!")

    for key, value in edit_order.dict(exclude_unset=True).items():
        setattr(order, key, value)
    session.commit()

    response = {
        "success": True,
        "code": 200,
        "message": "Sizning buyurtmangiz muvaffaqiyatli o'zgartirildi",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "totalprice": order.totalprice,
            "orderStatus": order.orderStatus.value,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            }
        }
    }
    return jsonable_encoder(response)


@orderRouter.patch("/{id}/order-status/edit", status_code=status.HTTP_200_OK)
async def order_status_edit(id: int, order_status: OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    print(user, '+++++++')

    order = session.query(Order).filter(Order.id == id).first()
    print(order, "++++++++")

    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{id} li ma'lumotni o'zgartira olmaysiz!")

    order.orderStatus = order_status.orderStatus
    session.commit()

    response = {
        "success": True,
        "code": 200,
        "message": "Order Status update is successfully",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "totalprice": order.totalprice,
            "orderStatus": order.orderStatus,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            }
        }
    }

    return jsonable_encoder(response)


@orderRouter.delete("/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def order_delete(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    order = session.query(Order).filter(Order.id == id).first()

    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{id} id li ma'lumotni o'chira olmaysiz")

    if order.orderStatus != "PENDING":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, siz yo'lga chiqgan yoki yetkazib berilgan buyurtmalarni ochira olmaysiz!")

    session.delete(order)
    session.commit()

    response = {
        "success": True,
        "code": 200,
        "message": "Order delete is successfully",
    }
    return jsonable_encoder(response)
