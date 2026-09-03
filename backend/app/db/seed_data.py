import random
from faker import Faker
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.db.models import Customer, Order, Payment, Ticket

fake = Faker()
session = SessionLocal()

def clear_existing():
    session.query(Ticket).delete()
    session.query(Payment).delete()
    session.query(Order).delete()
    session.query(Customer).delete()
    session.commit()

def seed():
    Base.metadata.create_all(bind=engine)
    clear_existing()

    # Customers
    customers = []
    for _ in range(200):
        c = Customer(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number()[:20],
        )
        customers.append(c)
    session.add_all(customers)
    session.commit()

    # Orders — deliberately reuse customers so some have 5+ orders
    statuses = ["Placed", "Shipped", "Delayed", "Delivered", "Cancelled"]
    orders = []
    for _ in range(800):
        status = random.choices(statuses, weights=[15, 20, 15, 40, 10])[0]
        o = Order(
            customer_id=random.choice(customers).customer_id,
            amount=round(random.uniform(200, 15000), 2),
            status=status,
            created_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )
        orders.append(o)
    session.add_all(orders)
    session.commit()

    # Payments — one per order, referencing valid order_ids
    pay_methods = ["Card", "UPI", "NetBanking"]
    pay_statuses = ["Success", "Refunded", "Failed"]
    payments = []
    for o in orders:
        pay = Payment(
            order_id=o.order_id,
            amount=o.amount,
            method=random.choice(pay_methods),
            status=random.choices(pay_statuses, weights=[85, 10, 5])[0],
            payment_date=o.created_at,
        )
        payments.append(pay)
    session.add_all(payments)
    session.commit()

    # Tickets — reference valid customers and orders
    subjects = ["Order delayed", "Wrong item received", "Refund request", "Damaged product", "Delivery query"]
    tickets = []
    for _ in range(100):
        ord_ = random.choice(orders)
        t = Ticket(
            customer_id=ord_.customer_id,  # keep customer/order consistent
            order_id=ord_.order_id,
            subject=random.choice(subjects),
            description=fake.paragraph(nb_sentences=3),
            status=random.choices(["Open", "In Progress", "Resolved"], weights=[30, 20, 50])[0],
            created_at=fake.date_time_between(start_date="-6M", end_date="now"),
        )
        tickets.append(t)
    session.add_all(tickets)
    session.commit()

    session.close()
    print("Seed complete: 200 customers, 800 orders, 800 payments, 100 tickets")

if __name__ == "__main__":
    seed()