"""
This module defines the SQLAlchemy models for the demographics data.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Demographics(Base):
    __tablename__ = "demographics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String, nullable=False)
    anemia_women = Column(Float, nullable=True)
    female_education_years = Column(Float, nullable=True)
    bmi_low = Column(Float, nullable=True)
    rural_population = Column(Float, nullable=True)
    child_mortality_rate = Column(Float, nullable=True)

class DemographicsStaging(Base):
    __tablename__ = "demographics_stg"
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    state = Column(String, nullable=False)
    anemia_women = Column(Float, nullable=True)
    female_education_years = Column(Float, nullable=True)
    bmi_low = Column(Float, nullable=True)
    rural_population = Column(Float, nullable=True)
    child_mortality_rate = Column(Float, nullable=True)
    
    upload_id = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False)