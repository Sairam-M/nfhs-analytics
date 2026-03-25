from fastapi import FastAPI, HTTPException, UploadFile
from csv import DictReader
from .database import get_states_from_db, upload_csv_to_pipeline, get_demographics_data_orm
import pandas as pd

app = FastAPI()

@app.get("/")
def home():
    return {"message": "NFHS Analytics API is running!"}


# API to upload csv file
@app.post("/upload")
async def upload_csv(file: UploadFile):
    if not file.filename.endswith('.csv'):
        # raise HTTPException with appropriate status code
        raise HTTPException(status_code=400, 
                            detail="Invalid file type. Please upload a CSV file.")
    # Handle empty File
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        # Raise HTTPException with appropriate status code and error message
        raise HTTPException(status_code=400, 
                            detail="Failed to process CSV file")

    row_count = len(df)
    upload_csv_to_pipeline(df)
    return {"message": "CSV file uploaded successfully!"}

@app.get("/demographics")
def get_demographics():
    data = get_demographics_data_orm()
    result = []
    for row in data:
        result.append({
            "id": row.id,
            "state": row.state,
            "anemia_women" : row.anemia_women,
            "female_education_years": row.female_education_years,
            "bmi_low": row.bmi_low,
            "rural_population": row.rural_population,
            "child_mortality_rate": row.child_mortality_rate
        })
    return {"data": result}

@app.get("/states")
def get_states():
    states = get_states_from_db()
    return {"states": states}