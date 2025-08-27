# backend/models.py - placeholder for SQLAlchemy models (expand later)
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    capacity = Column(Integer, nullable=True)
