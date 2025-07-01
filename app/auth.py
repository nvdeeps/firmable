from fastapi import Header, HTTPException, Depends
import os 
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ")[1]
    if token != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
