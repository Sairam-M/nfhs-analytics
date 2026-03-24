# Connect with Postgres SQL Database using SQLAlchemy
from fastapi import HTTPException

from fastapi import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from .models import Demographics
from sqlalchemy import select

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

def get_demographics_data_orm():
    # Using SQLAlchemy ORM to fetch data from the demographics table
    with Session(engine) as session:
        stmt = select(Demographics)
        return session.execute(stmt).scalars().all()
