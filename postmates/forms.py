from flask_wtf import Form
from wtforms import (DateTimeField, SelectField, StringField)
from wtforms.validators import URL, AnyOf, DataRequired, Regexp
# can be used to create form from sqlalchemy model directly
from wtforms.ext.sqlalchemy.orm import model_form

from postmates.models import Order


class OrderForm(Form):
    pickup_name = StringField('Pickup Name:', validators=[DataRequired()])
    pickup_address = StringField('Pickup Address:', validators=[DataRequired()])
    pickup_number = StringField('Pickup Number:', validators=[DataRequired()])
    
    dropoff_name = StringField('Dropoff Name:', validators=[DataRequired()])
    dropoff_address = StringField('Dropoff Address:', validators=[DataRequired()])
    dropoff_number = StringField('Dropoff Number:', validators=[DataRequired()])

    manifest = StringField('Manifest:', validators=[DataRequired()])

