from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT

from authRoutes import authRouter
from orderRoutes import orderRouter
from productRooutes import productRouter
from schemas import Settings

@AuthJWT.load_config
def get_config():
    return Settings()


app = FastAPI()
app.include_router(authRouter)
app.include_router(orderRouter)
app.include_router(productRouter)


