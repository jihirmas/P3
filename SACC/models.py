
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from database import Base

class Station(Base):
    __tablename__ = "station"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    
class Locker(Base):
    __tablename__ = "locker"
    
    id = Column(Integer, primary_key=True, index=True)
    personal_id = Column(Integer)
    state = Column(Integer)
    height = Column(Integer)
    width = Column(Integer)
    depth = Column(Integer)
    code = Column(String, unique=True, index=True, nullable=True)
    station_id = Column(Integer, ForeignKey("station.id"))
    
class Order(Base):
    __tablename__ = "order"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    depth = Column(Integer)
    
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    typeUser = Column(String)
    
class Reservation(Base):
    __tablename__ = "reservation"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    order_id = Column(Integer, ForeignKey("order.id"))
    locker_id = Column(Integer, ForeignKey("locker.id"))
    locker_personal_id = Column(Integer)
    station_id = Column(Integer, ForeignKey("station.id"))
    fecha = Column(DateTime)
    estado = Column(String)
    
    