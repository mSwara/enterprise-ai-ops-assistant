from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Customer, Order, Payment, Ticket

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/payments")
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()


@router.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()