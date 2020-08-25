from postmates import db


# DB for Orders
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String, primary_key=True)
    # pickup
    # number limited to 10 digits
    pickup_name = db.Column(db.String)
    pickup_address = db.Column(db.String)
    pickup_number = db.Column(db.String(10))
    # dropoff
    # number limited to 10 digits
    dropoff_name = db.Column(db.String)
    dropoff_address = db.Column(db.String)
    dropoff_number = db.Column(db.String(10))
    # Manifest
    manifest = db.Column(db.String)
