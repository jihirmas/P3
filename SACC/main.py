import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime



class Station(BaseModel):
    address: str
    
class Locker(BaseModel):
    state: int
    personal_id: int
    height: int
    width: int
    depth: int
    code: str
    station: List[Station]
    
class Order(BaseModel):
    name: str
    width: int
    height: int
    depth: int
    
class User(BaseModel):
    name: str
    email: str
    typeUser: str
    
class Reservation(BaseModel):
    user: List[User]
    order: List[Order]
    locker: List[Locker]
    locker_personal_id: int
    station: List[Station]
    fecha: datetime
    estado: str #activa, cancelada, finalizada


if __name__=="__main__":
    models.Base.metadata.create_all(bind=engine)
    uvicorn.run("app.app:app",port=8000, reload=True)
":"

