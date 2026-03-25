# Connect with Postgres SQL Database using SQLAlchemy
import uuid

from fastapi import HTTPException

from fastapi import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from .models import Demographics, DemographicsStaging
from sqlalchemy import select

import pandas as pd

DATABASE_URL = "postgresql://postgres:Sql123@localhost/nfhs_db"
engine = create_engine(DATABASE_URL)

def get_demographics_data():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM demographics"))
        return result.fetchall()

def upload_demographics_data(df):
    with engine.connect() as connection:
        try:
            df.to_sql("demographics", connection, if_exists="append", index=False)
        except Exception as e:
            logger.error(f"Failed to upload demographics data: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload demographics data")

def upload_csv_to_pipeline(df):
    upload_id = str(uuid.uuid4())
    df["upload_id"] = upload_id
    df["upload_time"] = pd.Timestamp.now()
    _upload_demographic_data_to_stg(df)
    _move_data_from_stg_to_main(upload_id)
    

def _upload_demographic_data_to_stg(df):
    with engine.connect() as connection:
        try:
            df.to_sql("demographics_stg", connection, if_exists="append", index=False)
        except Exception as e:
            logger.error(f"Failed to upload demographics data to staging: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload demographics data to staging")

def _move_data_from_stg_to_main(upload_id):
    data = _get_data_from_stg(upload_id)
    df = pd.DataFrame([{
        "state": row.state,
        "anemia_women": row.anemia_women,
        "female_education_years": row.female_education_years,
        "bmi_low": row.bmi_low,
        "rural_population": row.rural_population,
        "child_mortality_rate": row.child_mortality_rate
    } for row in data])

    _delete_demographics_data()
    upload_demographics_data(df)

def _get_data_from_stg(upload_id):
    with Session(engine) as session:
        stmt = select(DemographicsStaging).where(DemographicsStaging.upload_id == upload_id)
        return session.execute(stmt).scalars().all()

def _delete_demographics_data():
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM demographics"))
        except Exception as e:
            logger.error(f"Failed to delete demographics data: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete demographics data")

def get_demographics_data_orm():
    # Using SQLAlchemy ORM to fetch data from the demographics table
    with Session(engine) as session:
        stmt = select(Demographics)
        return session.execute(stmt).scalars().all()

def get_states_from_db():
    with Session(engine) as session:
        stmt = select(Demographics.state)
        return session.execute(stmt).scalars().all()
