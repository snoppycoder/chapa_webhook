
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from model.payment_request_body import PaymentRequest;
import httpx
import uuid
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from html import unescape
load_dotenv()
    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],  
)
@app.post("/payment")
async def payment_link_gen(req:PaymentRequest):
    uuid_id = str(uuid.uuid4())
    chapa_api_key = os.getenv("chapa_api_key")
    
    url = "https://api.chapa.co/v1/transaction/initialize"
    payload = {
    "amount": req.amount,
    "currency": "ETB",
    "email": req.email,
    "first_name": req.first_name,
    "last_name": req.last_name,
    "phone_number": req.phone_number,
    "tx_ref": uuid_id,
   "callback_url": (
    # f"https://chapa-webhook-bisho.onrender.com/payment/webhook"
    # f"?client_ref={req.client_ref}&hold_id={req.hold_id}"
    f"http://localhost:8000/payment/webhook"
    f"?client_ref={req.client_ref}&hold_id={req.hold_id}"
),

    "return_url": "https://danu-booking.vercel.app/passenger",
    "customization": {
    "title": "Danu booking",
    "description": "Danu booking"
    }
    }
    headers = {
    'Authorization': 'Bearer ' + chapa_api_key,
    'Content-Type': 'application/json'
    }
    print(req, "request")
      
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        data = response.json()
    return data
    # data = response.text
    # print(data)
@app.api_route("/payment/webhook", methods=["GET", "POST"])
async def webhook_call(req: Request):
    print(f"\n\n{req.url}\n\n")
    api_key = os.getenv("danu_api_key")
    
    headers = {
    "X-API-KEY": f"{api_key}", 
    'Content-Type': 'application/json'
    }
    try:
        payload = {unescape(k): unescape(v) for k, v in req.query_params.items()}
        payload = dict(req.query_params)
        if "amp;hold_id" in payload:
            payload["hold_id"] = payload.pop("amp;hold_id")
        print(f"{payload} payload")
        if payload.get("status") == "failed":
            return JSONResponse({"status": "Payment failed"}, status_code=400) 
        hold_id = payload.get("hold_id", "")
     
        url = f"https://danu.biisho.et/api/v1/passenger/holds/{hold_id}/confirm"
    
        async with httpx.AsyncClient() as client:
                response = await client.post(url, json={
                    "payment_reference": payload.get("trx_ref", ""),
                    "payment_method": "chapa-telebirr", # better name
                    "client_ref": payload.get("client_ref")} ,headers=headers)
                print(response)
                   
            # this where I call the confirm 
            
        #TODO MAYBE MARK THE DATABASE AS PAID IF SUCESSFULL
        return JSONResponse({"status": "Payment successful"}, status_code=200)

    except Exception as e:
        print(e)
        return JSONResponse({"status": "Payment failed"}, status_code=400)




    
