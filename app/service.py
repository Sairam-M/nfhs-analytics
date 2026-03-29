# service.py
from .database import get_demographics_data_orm, get_state_data

class DemographicsServiceConstants:
    ANEMIA_THRESHOLD = 50
    EDUCATION_THRESHOLD = 6

    ANEMIA_WEIGHT = 0.4
    CHILD_MORTALITY_WEIGHT = 0.3
    BMI_WEIGHT = 0.3

    SCORE_BAND_HIGH_THRESHOLD = 70
    SCORE_BAND_MODERATE_THRESHOLD = 40

    TOP_N_LIMIT = 20

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
    if state.anemia_women > DemographicsServiceConstants.ANEMIA_THRESHOLD and\
        state.female_education_years < DemographicsServiceConstants.EDUCATION_THRESHOLD:
            evaluation["risk"] = RiskLevel.HIGH
            evaluation["reason"] = "High anemia ({} %) and low education levels ({} y)".format(\
                state.anemia_women, state.female_education_years
                )
    elif state.anemia_women > DemographicsServiceConstants.ANEMIA_THRESHOLD:
        evaluation["risk"] = RiskLevel.MODERATE
        evaluation["reason"] = "High anemia levels ({} %)".format(state.anemia_women)
    elif state.female_education_years < DemographicsServiceConstants.EDUCATION_THRESHOLD:
        evaluation["risk"] = RiskLevel.MODERATE
        evaluation["reason"] = "Low education levels ({} y)".format(state.female_education_years)
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
    score = state.anemia_women * DemographicsServiceConstants.ANEMIA_WEIGHT +\
        state.child_mortality_rate * DemographicsServiceConstants.CHILD_MORTALITY_WEIGHT +\
        state.bmi_low * DemographicsServiceConstants.BMI_WEIGHT
    
    return round(score, 2)

def get_score_band(score):
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
    sorted_profiles = sorted(risk_profiles, key=lambda x: x["risk_score"], reverse=True)
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