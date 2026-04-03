# service.py
from .database import get_demographics_data_orm, get_state_data, upload_df_to_pipeline

import pandas as pd

class DemographicsServiceConstants:
    ANEMIA_THRESHOLD = 50
    EDUCATION_THRESHOLD = 6

    ANEMIA_WEIGHT = 0.4
    CHILD_MORTALITY_WEIGHT = 0.3
    BMI_WEIGHT = 0.3

    SCORE_BAND_HIGH_THRESHOLD = 70
    SCORE_BAND_MODERATE_THRESHOLD = 40

    TOP_N_LIMIT = 20

    REQUIRED_COLUMNS = ["state", "anemia_women", "bmi_low",
                        "child_mortality_rate","female_education_years",
                        "rural_population"]

class RiskLevel:
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

def evaluate_state_risk(state):
    evaluation = {
        "state": state.state,
        "anemia_women": state.anemia_women,
        "female_education_years": state.female_education_years
    }
    if (state.anemia_women and  state.anemia_women > DemographicsServiceConstants.ANEMIA_THRESHOLD) and\
        (state.female_education_years and \
         state.female_education_years < DemographicsServiceConstants.EDUCATION_THRESHOLD):
            evaluation["risk"] = RiskLevel.HIGH
            evaluation["reason"] = "High anemia ({} %) and low education levels ({} y)".format(\
                state.anemia_women, state.female_education_years
                )
    elif state.anemia_women and state.anemia_women > DemographicsServiceConstants.ANEMIA_THRESHOLD:
        evaluation["risk"] = RiskLevel.MODERATE
        evaluation["reason"] = "High anemia levels ({} %)".format(state.anemia_women)
    elif state.female_education_years and state.female_education_years < DemographicsServiceConstants.EDUCATION_THRESHOLD:
        evaluation["risk"] = RiskLevel.MODERATE
        evaluation["reason"] = "Low education levels ({} y)".format(state.female_education_years)
    elif state.anemia_women is None and state.female_education_years is None:
        evaluation["risk"] = None
        evaluation["reason"] = "Missing anemia_women and female_education_years data"
    else:
        evaluation["risk"] = RiskLevel.LOW
        evaluation["reason"] = "Anemia and education levels are within acceptable ranges"
    
    return evaluation

def get_high_risk_states_with_reason():
    state_list = get_demographics_data_orm()
    # Filter states based on criteria
    # keep state, anemia and education columns
    high_risk_states = []
    for state in state_list:
        evaluation = evaluate_state_risk(state)
        if evaluation["risk"] == RiskLevel.HIGH:
            high_risk_states.append(evaluation)
    return high_risk_states

# service.py
def calculate_risk_score(state):
    if state.anemia_women is None or\
        state.child_mortality_rate is None or\
        state.bmi_low is None:
            return None 
    score = state.anemia_women * DemographicsServiceConstants.ANEMIA_WEIGHT +\
        state.child_mortality_rate * DemographicsServiceConstants.CHILD_MORTALITY_WEIGHT +\
        state.bmi_low * DemographicsServiceConstants.BMI_WEIGHT
    
    return round(score, 2)

def get_score_band(score):
    if score is None:
        return None
    if score >= DemographicsServiceConstants.SCORE_BAND_HIGH_THRESHOLD:
        return RiskLevel.HIGH
    elif score >= DemographicsServiceConstants.SCORE_BAND_MODERATE_THRESHOLD:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.LOW

def get_risk_profile_for_state(state):
    score = calculate_risk_score(state)
    score_band = get_score_band(score)
    return {
        "state": state.state,
        "anemia_women": state.anemia_women,
        "bmi_low": state.bmi_low,
        "child_mortality_rate": state.child_mortality_rate,
        "risk_score": score,
        "score_band": score_band
    }

def get_risk_scores_for_all_states():
    state_list = get_demographics_data_orm()
    risk_profiles = []
    for state in state_list:
        risk_profile = get_risk_profile_for_state(state)
        risk_profiles.append(risk_profile)
    return risk_profiles

def get_top_n_states_by_risk_score(n=5):
    n = max(n, 1)  # Ensure n is at least 1
    n = min(DemographicsServiceConstants.TOP_N_LIMIT, n)
    risk_profiles = get_risk_scores_for_all_states()
    non_null_risk_profiles = filter(lambda risk: risk["risk_score"] is not None, risk_profiles)
    sorted_profiles = sorted(non_null_risk_profiles, key=lambda x: x["risk_score"], reverse=True)
    sorted_profiles += filter(lambda risk: risk["risk_score"] is None, risk_profiles)
    return sorted_profiles[:n]

def get_state_profile_service(state_name):
    state = get_state_data(state_name)
    state_profile = evaluate_state_risk(state)
    score = calculate_risk_score(state)
    score_band = get_score_band(score)
    return {
        "state": state.state,
        "metrics": {
            "anemia_women": state.anemia_women,
            "bmi_low": state.bmi_low,
            "child_mortality_rate": state.child_mortality_rate,
            "female_education_years": state.female_education_years,
            "rural_population": state.rural_population
        },
        "risk_category": state_profile["risk"],
        "reason": state_profile["reason"],
        "risk_score":score,
        "score_band": score_band
    }


def drop_extra_column(df):
    # Remove extra columns if any
    existing_columns = set(df.columns)
    required_columns = set(DemographicsServiceConstants.REQUIRED_COLUMNS)

    extra_columns = existing_columns - required_columns
    df = df.drop(columns = list(extra_columns))

    return df

def clean_state_column(df):
    df = df[df["state"].notna()].copy()

    df["state"] = df["state"].astype(str).str.strip()
    df = df[
            (df["state"] != "") &
            (df["state"].str.lower() != "nan")
        ]

    return df

def clean_numeric_columns(df, numeric_cols):
    df[numeric_cols] = df[numeric_cols].apply(
        pd.to_numeric, errors="coerce")

    # 4. Handle invalid values
    df[numeric_cols] = df[numeric_cols].mask(df[numeric_cols] < 0)
    return df

def validate_and_upload_df(df):
    df = drop_extra_column(df)
    df = clean_state_column(df)
    numeric_cols = set(DemographicsServiceConstants.REQUIRED_COLUMNS) - {"state"}
    df = clean_numeric_columns(df, list(numeric_cols))
    upload_df_to_pipeline(df)