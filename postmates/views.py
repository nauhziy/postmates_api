import babel
import dateutil.parser
from flask import flash, redirect, render_template, request, url_for

import os
from postmates import app, db
from postmates.forms import OrderForm
from postmates.models import Order, api, location, delivery_quote, delivery, postmates_api_exception

# Please configure these if you wish to run it on your own local machine
app.config['SECRET_KEY'] = os.environ.get("secret_key")
postmates_api_key = os.environ.get("postmates_api_key")
customer_id = os.environ.get("customer_id")
api = api(postmates_api_key, customer_id)

# ----------------------------------------------------------------------------#
#  Jinja Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
#  Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/orders')
def orders():
    orders = Order.query.all()
    data = []
    for order in orders:
        data.append({
            "id": order.id,
            "pickup_name": order.pickup_name,
            "pickup_address": order.pickup_address,
            "pickup_number": order.pickup_number,
            "dropoff_name": order.dropoff_name,
            "dropoff_address": order.dropoff_address,
            "dropoff_number": order.dropoff_number,
            "manifest": order.manifest,
            "tracker_url": f"https://postmates.com/track/{order.id}"
        })
    return render_template('pages/orders.html', orders=data)


@app.route('/orders/create')
def create_orders():
    # renders form. do not touch.
    form = OrderForm()
    return render_template('forms/new_order.html', form=form)


@app.route('/orders/create', methods=['POST'])
def create_order_submission():
    try:
        new_order_data = request.form.to_dict()
        pickup = location(new_order_data['pickup_name'], new_order_data['pickup_address'], new_order_data['pickup_number'])
        dropoff = location(new_order_data['dropoff_name'], new_order_data['dropoff_address'], new_order_data['dropoff_number'])
        new_quote = delivery_quote(api, pickup, dropoff)

        new_delivery = delivery(api, new_order_data['manifest'], pickup, dropoff, new_quote)
        new_delivery.create()

        new_order_data['id'] = new_delivery.delivery_id
        new_order = Order(**new_order_data)

        db.session.add(new_order)
        db.session.commit()
        # on successful db insert, flash success
        flash('New order was successfully listed with ID {}!'.format(new_order.id))
        return redirect(url_for('orders'))

    # rollback if fail to avoid potential implicit commits
    except Exception as e:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead.
        flash(f"An error occurred: {e}", "error")
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
