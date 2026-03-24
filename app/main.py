from fastapi import FastAPI, HTTPException, UploadFile
from csv import DictReader
from .database import get_demographics_data, upload_demographics_data
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
    upload_demographics_data(df)
    return {"message": "CSV file uploaded successfully!"}

@app.get("/demographics")
def get_demographics():
    data = get_demographics_data()
    result = []
    for row in data:
        result.append({
            "id": row[0],
            "state": row[1],
            "anemia_women" : row[2],
            "female_education_years": row[3],
            "bmi_low": row[4],
            "rural_population": row[5],
            "child_morality_rate": row[6]
        })
    return {"data": result}