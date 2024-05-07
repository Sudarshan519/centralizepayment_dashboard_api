from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException,Request,status
from firebase_admin import credentials, firestore, initialize_app
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import base64


# Create FastAPI instance
app = FastAPI()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


cred = credentials.Certificate(json.loads(os.getenv("ADMIN_SDK"))) #'rockstar-dashboard-710d7-firebase-adminsdk-3hhjb-7a0b4953ce.json')
initialize_app(cred)
security = HTTPBearer()
# Firestore client
db = firestore.client()


def get_user(token: str):
    if token.credentials ==os.getenv('oauthtoken'):
        return token
    return None

def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Replace this with your own token verification logic
    user = get_user(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

# Define endpoint to get document by email
@app.get("/getBillingsByEmail/{email}")
async def get_doc_by_email(token: Annotated[str, Depends(security)],email: str,request:Request):
    user = get_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Query Firestore collection based on email
        docs_ref = db.collection('billing').where('user', '==', email).limit(1)
        docs = docs_ref.get()

        # Check if any documents match the query result
        for doc in docs:
            return doc.to_dict()

        # If no document found
        raise HTTPException(status_code=404, detail="No billing found for user." )

    except Exception as e:
        raise e#HTTPException(status_code=500, detail=str(e))
    
