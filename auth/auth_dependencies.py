from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401,
                                          detail="Invalid authentication credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email= payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    
    except JWTError:
        raise credentials_exception
