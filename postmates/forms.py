from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class OrderForm(Form):
    pickup_name = StringField('Pickup Name:', validators=[DataRequired()])
    pickup_address = StringField('Pickup Address:', validators=[DataRequired()])
    pickup_number = StringField('Pickup Number:', validators=[DataRequired()])
    dropoff_name = StringField('Dropoff Name:', validators=[DataRequired()])
    dropoff_address = StringField('Dropoff Address:', validators=[DataRequired()])
    dropoff_number = StringField('Dropoff Number:', validators=[DataRequired()])
    manifest = StringField('Manifest:', validators=[DataRequired()])
