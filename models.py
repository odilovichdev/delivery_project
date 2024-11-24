from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String(50))
    password = Column(Text, nullable=False)
    isStaff = Column(Boolean, default=False)
    isActive = Column(Boolean, default=False)
    orders = relationship("Order", back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Float)
    orders = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"


class Order(Base):
    ORDER_STATUS = (
        ("PENDING", "pending"),
        ("IN_TRANSIT", "in_transit"),
        ("DELIVERED", "delivered")
    )
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=True)
    orderStatus = Column(ChoiceType(ORDER_STATUS), default="PENDING")
    totalprice = Column(Float, default=0)
    userId = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates='orders') # ToDo
    productId = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, quantity={self.quantity}, price={self.totalprice})>"
