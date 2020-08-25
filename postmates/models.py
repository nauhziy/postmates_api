from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

from postmates import db

import json
import requests
from datetime import datetime
from dateutil import tz
import os

### DB for Orders ###
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

### General Methods ###
# Parses the date 
def date_parse_to_utc(date):
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    dt_utc = dt.replace(tzinfo=tz.tzutc())
    return dt_utc.strftime("%Y-%m-%d %H:%M:%S")


### General Classes ###
# Contains the functions used to post/get from postmates API
class api(object):
    base_url = "https://api.postmates.com"
    
    def __init__(self, key, customer_id):
        self.key = key
        self.customer_id = customer_id
        self.delivery_id = None
        self.quote_id = None
    
    ### Delivery
    def post_create_delivery(self, delivery):
        req_url = f"{self.base_url}/v1/customers/{self.customer_id}/deliveries"

        req_params = delivery.post_data()

        response = requests.post(req_url, data=req_params, auth=(self.key, ""))
        return response


    def get_delivery(self):
        req_url = f"{self.base_url}/v1/customers/{self.customer_id}/deliveries/{self.delivery_id}"

        response = requests.get(req_url, data=req_params, auth=(self.key, ""))
        return response

    def post_update_delivery(self, tip_by_customer):
        req_url = f"{self.base_url}/v1/customers/{self.customer_id}/deliveries/{self.delivery_id}"
        
        req_params = {
            "tip_by_customer" : tip_by_customer
        }

        response = requests.post(req_url, data=req_params, auth=(self.key, ""))
        return response

    def post_cancel_delivery(self):
        req_url = f"{self.base_url}/v1/customers/{self.customer_id}/deliveries/{self.delivery_id}/cancel"

        response = requests.post(req_url, data=req_params, auth=(self.key, ""))
        return response

    def get_list_delivery(self):
        req_url = f"{self.base_url}/v1/customers/{self.customer_id}/deliveries"

        response = requests.post(req_url, data=req_params, auth=(self.key, ""))
        return response

    ### Quote
    def post_create_quote(self, pickup_addess, dropoff_addess):
        req_url = f"{self.base_url}/v1/customers/{self.customer_id}/delivery_quotes"

        req_params = {
            "pickup_address" : pickup_addess,
            "dropoff_address" : dropoff_addess
        }

        response = requests.post(req_url, data=req_params, auth=(self.key, ""))
        return response

class location(object):
    def __init__(self, name, address, phone_number, business_name=None, notes=None):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.business_name = business_name
        self.notes = notes

    def check_validity(self):
        if self.name is None or self.address is None or self.phone_number is None:
          return False
        return True

    def __repr__(self):
        s = []
        s.append(f"### Location ###")
        s.append(f"Name (required): {self.name}")
        s.append(f"Address (required): {self.address}")
        s.append(f"Phone Number (required): {self.phone_number}")
        s.append(f"Business Name (optional):{self.business_name}")
        s.append(f"Notes (optional): {self.notes}")
        return "\n".join(s)

    def post_data(self, prefix):
        post_data = {}

        post_data["%s_name" % prefix] = self.name
        post_data["%s_address" % prefix] = self.address
        post_data["%s_phone_number" % prefix] = self.phone_number
        post_data["%s_business_name" % prefix] = self.business_name
        post_data["%s_notes" % prefix] = self.notes

        return post_data

# Get a delivery quote
class delivery_quote(object):
    def __init__(self, api, pickup, dropoff):
        quote = api.post_create_quote(pickup.address, dropoff.address)
        result = quote.json()

        if result['kind'] == 'error':
            raise postmates_api_exception(result['message'] + '\n' + str(result['params']))

        self.kind = result["kind"]
        self.quote_id = result["id"]
        self.created = date_parse_to_utc(result["created"])
        self.expires = date_parse_to_utc(result["expires"])
        self.fee = result["fee"]
        self.currency = result["currency"]
        self.currency_type = result["currency_type"]
        self.dropoff_eta = date_parse_to_utc(result["dropoff_eta"])
        self.duration = result["duration"]
        self.pickup_duration = result["pickup_duration"]
        self.pickup = pickup
        self.dropoff = dropoff

    @property
    def expired(self):
        utc_now = datetime.utcnow().replace(tzinfo=tz.tzutc())
        expiry = datetime.strptime(self.expires, "%Y-%m-%d %H:%M:%S")
        expiry_utc = expiry.replace(tzinfo=tz.tzutc())
        return utc_now > expiry_utc

    def __repr__(self):
        s = []
        s.append(f"### Delivery Quote ###")
        s.append(f"Quote Id: {self.quote_id}")
        s.append(f"Pickup: {self.pickup.address}")
        s.append(f"Dropoff: {self.dropoff.address}")
        s.append(f"Expires: {self.expires}")
        s.append(f"Fee: {self.fee}")
        s.append(f"Currency: {self.currency}")
        s.append(f"Currency Type:{self.currency_type}")
        s.append(f"Dropoff ETA: {self.dropoff_eta}")
        s.append(f"Duration: {self.duration}")
        s.append(f"Pickup Duration: {self.pickup_duration}")
        s.append(f"Expired: {self.expired}")
        return "\n".join(s)

# Create and manipulate Delivery
class delivery(object):
    delivery_status = {
    "pending" : "pending",
    "pickup" : "pickup",
    "pickup_complete" : "pickup_complete",
    "dropoff" : "dropoff",
    "canceled" : "canceled",
    "returned" : "returned",
    "ongoing" : "ongoing"
    }

    def __init__(self, api, manifest, pickup, dropoff, delivery_quote):
        self.api = api
        self.manifest = manifest
        self.pickup = pickup
        self.dropoff = dropoff
        self.quote = delivery_quote

        self.delivery_id = None
        self.status = None
        self.complete = False
        self.pickup_eta = None
        self.dropoff_eta = None
        self.dropoff_deadline = None
        self.fee = None
        self.currency = None
        self.courier = None

    def create(self):
        # ensure that values are valid prior to posting delivery creation request
        if not self.pickup.check_validity():
            raise postmates_api_exception(f"Pickup details are missing\n{pickup}")

        if not self.dropoff.check_validity():
            raise postmates_api_exception(f"Dropoff details are missing\n{dropoff}")

        if self.status is not None:
            raise postmates_api_exception(f"Delivery has already been submitted")

        if self.quote and self.quote.expired:
            raise postmates_api_exception(f"Delivery quote has expired")

        delivery_data = self.api.post_create_delivery(self)
        self.update_delivery(delivery_data)

    def update_status(self):
        if self.delivery_id is None:
            return

        delivery_data = self.api.get_delivery(self.delivery_id)
        self.update_delivery(delivery_data)

    def post_cancel_delivery(self):
        if self.status not in ("dropoff", "canceled"):
            raise postmates_api_exception("Can only cancel deliveries not yet picked up")

        delivery_data = self.api.post_cancel_delivery(self.delivery_id)
        self.update_delivery(delivery_data)

    def update_delivery(self, data):
        data = data.json()

        if data['kind'] == 'error':
            raise postmates_api_exception(data['message'] + '\n' + str(data['params']))

        self.delivery_id = data["id"]
        self.status = data["status"]
        self.complete = data["complete"]
        self.pickup_eta = date_parse_to_utc(data["pickup_eta"])
        self.dropoff_eta = date_parse_to_utc(data["dropoff_eta"])
        self.dropoff_deadline = date_parse_to_utc(data["dropoff_deadline"])
        self.fee = data["fee"]
        self.currency = data["currency"]
        self.courier = data["courier"]

    def post_data(self):

        post_data = {}

        post_data["manifest"] = self.manifest
        post_data.update(self.pickup.post_data("pickup"))
        post_data.update(self.dropoff.post_data("dropoff"))

        if self.quote:
            post_data["quote_id"] = self.quote.quote_id
        return post_data

    def __repr__(self):
        s = []
        s.append("Postmates Delivery")
        s.append(f"Manifest (required): {self.manifest}")
        s.append("Pickup --------------")
        s.append(str(self.pickup))
        s.append("Dropoff --------------")
        s.append(str(self.dropoff))

        if self.status != None:
            s.append("Status --------------")
            s.append(f"Delivery ID: {self.delivery_id}")
            s.append(f"Status: {self.status}")
            s.append(f"Complete: {self.complete}")
            s.append(f"Pickup ETA: {_to_local_tz(self.pickup_eta)}")
            s.append(f"Dropoff ETA: {_to_local_tz(self.dropoff_eta)}")
            s.append(f"Dropoff Deadline: {_to_local_tz(self.dropoff_deadline)}")
            s.append(f"Fee: ${self.fee//100.0}.{self.fee%100.0} {self.currency}")
            s.append(f"Courier: {self.courier}")

        return "\n".join(s)

class postmates_api_exception(Exception):

    def __init__(self, message):
        if isinstance(message, str):
            super(postmates_api_exception, self).__init__(message)
        else:
            super(postmates_api_exception, self).__init__(message["message"])
            self.kind = message["kind"]
            self.code = message["code"]