from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150), unique=True)
    phone = Column(String(30))

    tickets = relationship("Ticket", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    amount = Column(Float, nullable=False)
    status = Column(String(30), default="Pending")
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer")
    payments = relationship("Payment", back_populates="order")

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    amount = Column(Float, nullable=False)
    method = Column(String(30))
    status = Column(String(30))
    payment_date = Column(DateTime, default=datetime.now)

    order = relationship("Order", back_populates="payments")


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True)
    subject = Column(String(150))
    description = Column(Text)
    status = Column(String(30), default="Open")
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer", back_populates="tickets")