from fastapi import FastAPI, Request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn
from fastapi.responses import JSONResponse

app = FastAPI()

# Database config - adjust these values
DATABASE_URL = "mysql+pymysql://root:monika123@localhost:3306/dialogflow_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define the database model
class ServiceRequest(Base):
    __tablename__ = 'service_requests_2'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    customer_name = Column(String(255), nullable=True)
    service_type = Column(String(255), nullable=True)
    contact_number = Column(String(20), nullable=True)

Base.metadata.create_all(bind=engine)

# Utility to extract session ID
def extract_session_id(output_contexts):
    for context in output_contexts:
        if "name" in context:
            parts = context["name"].split("/")
            if "sessions" in parts:
                return parts[parts.index("sessions") + 1]
    return "unknown_session"

# Utility to get or create a ServiceRequest row
def get_or_create_request(session_id):
    db = SessionLocal()
    request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
    if not request:
        request = ServiceRequest(session_id=session_id)
        db.add(request)
        db.commit()
        db.refresh(request)
    db.close()
    return request

# Intent handlers
#def handle_service_intent(parameters: dict, session_id: str):
 #   db = SessionLocal()
  #  request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
   # if not request:
    #    request = ServiceRequest(session_id=session_id)

    #request.customer_name = parameters.get("name", request.customer_name)
 #   request.service_type = parameters.get("service", request.service_type)

 #   db.add(request)
 #   db.commit()
 #   db.close()

  #  return {
  #      "fulfillmentText": f"Thanks {request.customer_name}, your request for {request.service_type} service has been recorded."
   # }

def handle_service_intent(parameters: dict, session_id: str):
    db = SessionLocal()
    request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
    if not request:
        request = ServiceRequest(session_id=session_id)

    request.service_type = parameters.get("service", request.service_type)
    db.add(request)
    db.commit()
    db.close()

    return {
        "fulfillmentText": f"Your request for {request.service_type} service has been recorded. We will contact you soon!"
    }


#def handle_name_intent(parameters: dict, session_id: str):
#    name = parameters.get("name", "Customer")
#   db = SessionLocal()
 #   request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
 #   if not request:
 #       request = ServiceRequest(session_id=session_id)

  #  request.customer_name = name
 #   db.add(request)
 #   db.commit()
 #   db.close()

 #   return {
 #       "fulfillmentText": f"Thanks {name}, I’ve saved your name."
 #   }

def handle_name_intent(parameters: dict, session_id: str):
    name = parameters.get("name", "Customer")
    db = SessionLocal()
    request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
    if not request:
        request = ServiceRequest(session_id=session_id)

    request.customer_name = name
    db.add(request)
    db.commit()
    db.close()

    return {
        "fulfillmentText": f"Thanks {name}, can I have your contact number?"
    }


#def handle_contact_intent(parameters: dict, session_id: str):
#    contact = parameters.get("phone-number", "Not Provided")
#    db = SessionLocal()
#    request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
#    if not request:
#        request = ServiceRequest(session_id=session_id)

#    request.contact_number = contact
#    db.add(request)
#    db.commit()
 #   db.close()

 #   return {
 #       "fulfillmentText": f"Thanks! I've saved your contact number: {contact}."
 #   }

def handle_contact_intent(parameters: dict, session_id: str):
    contact = parameters.get("phone-number", "Not Provided")
    db = SessionLocal()
    request = db.query(ServiceRequest).filter_by(session_id=session_id).first()
    if not request:
        request = ServiceRequest(session_id=session_id)

    request.contact_number = contact
    db.add(request)
    db.commit()
    db.close()

    return {
        "fulfillmentText": f"Thanks! I've saved your contact number: {contact}. What type of service do you need?"
    }


# Main webhook route
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    query_result = body.get("queryResult", {})
    intent_name = query_result.get("intent", {}).get("displayName", "")
    print(f"🧠 Received intent: {intent_name}")  #added
    parameters = query_result.get("parameters", {})
    output_contexts = query_result.get("outputContexts", [])
    session_id = extract_session_id(output_contexts)

    if intent_name == "Default Welcome Intent":
        return {"fulfillmentText": "Welcome! How can I assist you today?"}

    elif intent_name == "Default Fallback Intent":
        return {"fulfillmentText": "Sorry, I didn't understand that. Can you please repeat?"}

    elif intent_name == "service.intent":
        return handle_service_intent(parameters, session_id)

    elif intent_name == "name.intent":
        return handle_name_intent(parameters, session_id)

    elif intent_name == "contactn.intent":
        return handle_contact_intent(parameters, session_id)

    else:
        return {"fulfillmentText": "Intent not handled yet."}

# Optional: for running directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

@app.post("/")
async def root_fallback():
    return JSONResponse(status_code=404, content={"message": "Incorrect path. Use /webhook"})
