from flask import Flask, request

import sqlalchemy
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

import openai

app = Flask(__name__)

db = sqlalchemy.create_engine("sqlite:///db1.db")

Base = declarative_base()

OPENAI_API_KEY = "sk-abcdef1234567890abcdef1234567890abcdef12"

class SavedOrder(Base):
    __tablename__ = "saved_order"
    order_id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=True)
    email = Column(String)
    address = Column(String)
    item_name = Column(String, nullable=True)
    current_variant_id = Column(Integer)
    product_id = Column(Integer)
    pincode = Column(String)
    phone_valid = Column(Boolean)
    address_valid = Column(Boolean)
    
    
Base.metadata.create_all(db)

@app.route("/variants")
def variant_api():
    pass

@app.route("/webhook")
def webhook():
    Session = sessionmaker()
    Session.configure(bind=db)
    session = Session()
    
    request_data = request.json
    
    order_id = request_data['order']['id']
    email = request_data['order']['contact_email']
    phone = request_data['order']["customer"]["default_address"]["phone"]
    # address = request_data['order']["customer"]["default_address"]["address1"] \
    #     + ", " \
    #     + request_data['order']["customer"]["default_address"]["address2"] \
    #     + ", " \
    #     + request_data['order']["customer"]["default_address"]["zip"]
    if request_data['order']["customer"]["default_address"]["address2"] is not None:
        address = request_data['order']["customer"]["default_address"]["address1"] \
            + ", " \
            + request_data['order']["customer"]["default_address"]["address2"] \
            + ", " \
            + request_data['order']["customer"]["default_address"]["zip"]
    else:
        address = request_data['order']["customer"]["default_address"]["address1"] \
            + ", " \
            + request_data['order']["customer"]["default_address"]["zip"]
    
    pincode = request_data['order']["customer"]["default_address"]["zip"]
    item_name = request_data['order']['line_items'][0]['name']
    product_id = request_data['order']['line_items'][0]['id']
    current_variant_id = request_data['order']['line_items'][0]['variant_id']
    
    order = SavedOrder(
        order_id=order_id,
        phone=phone,
        email=email,
        address=address,
        item_name=item_name,
        current_variant_id=current_variant_id,
        product_id=product_id,
        pincode=pincode
    )
    
    order.address_valid = validate_address(address)
    order.phone_valid = validate_phone_number(phone)
    
    session.add(order)
    session.commit()
    
    return {
        "meta": {
            "status": "SUCCESS",
            "success": True
        }, 
        "result": {
            "order_id": order_id,
            "phone": phone,
            "email": email,
            "address": address,
            "item_name": item_name,
            "current_variant_id": current_variant_id,
            "product_id": product_id,
            "pincode": pincode,
            "address_valid": order.address_valid,
            "phone_valid": order.phone_valid
        }
    }
    
def validate_phone_number(pincode):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Answer only in true or false."
            },
            {
                "role": "user",
                "content": f"Is this phone number valid? {pincode}"
            }
        ]
    )
    print(response)

    return response.choices[0].message.content.strip().lower() == "true"

def validate_address(address):
    return True
    

if __name__ == '__main__':    
    app.run("127.0.0.1", 8000)