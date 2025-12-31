from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: float
    email: str
    first_name: str
    last_name: str
    phone_number:str
    # client_ref:str
    hold_id:str
    # payment_method:str
    