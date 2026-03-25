# service.py
from .database import get_demographics_data_orm

class DemographicsServiceConstants:
    ANEMIA_THRESHOLD = 50
    EDUCATION_THRESHOLD = 6

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
            evaluation["reason"] = "High anemia ({}) and low education levels ({})".format(\
                state.anemia_women, state.female_education_years
                )
    elif state.anemia_women > DemographicsServiceConstants.ANEMIA_THRESHOLD:
        evaluation["risk"] = RiskLevel.MODERATE
        evaluation["reason"] = "High anemia levels ({})".format(state.anemia_women)
    elif state.female_education_years < DemographicsServiceConstants.EDUCATION_THRESHOLD:
        evaluation["risk"] = RiskLevel.MODERATE
        evaluation["reason"] = "Low education levels ({})".format(state.female_education_years)
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
