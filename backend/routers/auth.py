from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import database, models, schemas, auth, crud

router = APIRouter(tags=["Authentication"])

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Try to authenticate as employee
    user = crud.get_employee_by_email(db, form_data.username)
    role = "employee" # Default or logic to determine
    if not user:
        # Try as client
        user = crud.get_client_by_email(db, form_data.username)
        role = "client"
        
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If user has a specific role attribute, use it, else use the inferred one
    if hasattr(user, 'role'): 
        user_role = user.role
    else:
        user_role = "client"

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user_role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.Employee) # Adjust response model as needed or use Union
async def read_users_me(current_user = Depends(auth.get_current_active_user)):
    return current_user
