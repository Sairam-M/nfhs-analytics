from fastapi import FastAPI, HTTPException, UploadFile
from csv import DictReader
from .database import DatabaseException, StateNotFoundException, get_states_from_db, get_demographics_data_orm
from .service import get_high_risk_states_with_reason, get_risk_scores_for_all_states, get_state_profile_service, get_top_n_states_by_risk_score,\
    validate_and_upload_df, DemographicsServiceConstants
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import pandas as pd
import os

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        # Raise HTTPException with appropriate status code and error message
        raise HTTPException(status_code=400, 
                            detail="Failed to process CSV file")
    
    # Data validation
    missing = set(DemographicsServiceConstants.REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing}"
        )
    row_count = len(df)
    try:
        validate_and_upload_df(df)
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
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

@app.get("/high-risk-states")
def get_high_risk_states():
    # Implementation for fetching high-risk states
    states = get_high_risk_states_with_reason()
    return {"high_risk_states": states}

@app.get("/risk-scores")
def get_risk_scores():
    risk_scores = get_risk_scores_for_all_states()
    return {"risk_scores": risk_scores}

@app.get("/top-states-by-score")
def get_top_states_by_score(n: int = 5):
    top_states = get_top_n_states_by_risk_score(n)
    return {"top_states_by_score": top_states}

@app.get("/state-profile/{state_name}")
def get_state_profile(state_name: str):
    try:
        state_profile = get_state_profile_service(state_name)
    except StateNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    return state_profile