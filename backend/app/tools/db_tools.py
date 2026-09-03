from app.db.session import SessionLocal
from app.db.models import Customer, Order, Payment, Ticket


def get_customer(customer_id: int):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()

        if not customer:
            return {"error": "Customer not found"}

        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
        }
    finally:
        db.close()


def get_customer_orders(customer_id: int):
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(
            Order.customer_id == customer_id
        ).all()

        return [
            {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "amount": order.amount,
                "status": order.status,
                "created_at": str(order.created_at),
            }
            for order in orders
        ]
    finally:
        db.close()


def get_order_payment(order_id: int):
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()

        if not payment:
            return {"error": "Payment not found"}

        return {
            "payment_id": payment.payment_id,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "method": payment.method,
            "status": payment.status,
            "payment_date": str(payment.payment_date),
        }
    finally:
        db.close()


def get_customer_tickets(customer_id: int):
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).filter(
            Ticket.customer_id == customer_id
        ).all()

        return [
            {
                "ticket_id": ticket.ticket_id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "subject": ticket.subject,
                "description": ticket.description,
                "status": ticket.status,
                "created_at": str(ticket.created_at),
            }
            for ticket in tickets
        ]
    finally:
        db.close()


def create_ticket(customer_id: int, subject: str, description: str, order_id: int = None):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        if not customer:
            return {"error": f"Customer {customer_id} not found"}

        if order_id is not None:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if not order:
                return {"error": f"Order {order_id} not found"}

        ticket = Ticket(
            customer_id=customer_id,
            order_id=order_id,
            subject=subject,
            description=description,
            status="Open",
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return {
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "order_id": ticket.order_id,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status,
            "created_at": str(ticket.created_at),
        }
    finally:
        db.close()        


import logging

logger = logging.getLogger("email_simulator")

def send_email(customer_id: int, subject: str, body: str):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        if not customer:
            return {"error": f"Customer {customer_id} not found"}

        # Simulated send — logs instead of using a real email provider
        logger.info(
            f"[SIMULATED EMAIL] To: {customer.email} | Subject: {subject} | Body: {body}"
        )

        return {
            "status": "sent",
            "to": customer.email,
            "customer_id": customer.customer_id,
            "subject": subject,
            "body": body,
        }
    finally:
        db.close()
