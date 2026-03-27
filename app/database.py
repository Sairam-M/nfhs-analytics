# Connect with Postgres SQL Database using SQLAlchemy
import uuid
import logging

from fastapi import HTTPException

from fastapi import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from .models import Demographics, DemographicsStaging
from sqlalchemy import select

from dotenv import load_dotenv

import pandas as pd
import os

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
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
            raise DatabaseException("Failed to upload demographics data")

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
            logger.exception(f"Failed to upload demographics data to staging: {e}")
            raise DatabaseException("Failed to upload demographics data to staging")

def _move_data_from_stg_to_main(upload_id):
    DELETE_QUERY = "DELETE FROM demographics"
    INSERT_QUERY = """INSERT INTO demographics
                        (state, anemia_women, female_education_years, 
                        bmi_low, rural_population, child_mortality_rate)
                        SELECT state, anemia_women, female_education_years,
                        bmi_low, rural_population, child_mortality_rate
                        FROM demographics_stg
                        WHERE upload_id = :upload_id
                        """
    with engine.begin() as connection:
        try:
            connection.execute(text(DELETE_QUERY))
            logger.info("Deleted existing data from demographics table")

            connection.execute(text(INSERT_QUERY), {"upload_id": upload_id})
            logger.info("Inserted new data into demographics table from staging")
        except Exception as e:
            logger.exception(f"Failed to delete and insert demographics data: {e}")
            raise DatabaseException("Failed to delete and insert demographics data")

def get_demographics_data_orm():
    # Using SQLAlchemy ORM to fetch data from the demographics table
    with Session(engine) as session:
        stmt = select(Demographics)
        return session.execute(stmt).scalars().all()

def get_states_from_db():
    with Session(engine) as session:
        stmt = select(Demographics.state)
        return session.execute(stmt).scalars().all()

def get_state_data(state_name):
    with Session(engine) as session:
        stmt = select(Demographics).where(Demographics.state == state_name)
        result = session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise StateNotFoundException(f"State '{state_name}' not found")
        return result

class StateNotFoundException(Exception):
    pass

class DatabaseException(Exception):
    pass