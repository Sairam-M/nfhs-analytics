import pytest
from app import service
from .test_utility import upload_data_for_testing,\
                        VALID_DATA_1,\
                        DIRTY_STATE_DATA,\
                        DIRTY_NUMERIC_DATA,\
                        EXTRA_COLUMN_DATA
import pandas as pd

class State:
    def __init__(self, state, anemia_women=None, 
                 female_education_years=None, 
                 bmi_low=None, 
                 rural_population=None, 
                 child_mortality_rate=None):
        self.state = state
        self.anemia_women = anemia_women
        self.female_education_years = female_education_years
        self.bmi_low = bmi_low
        self.rural_population = rural_population
        self.child_mortality_rate = child_mortality_rate

# -------- evaluate_state_risk --------
def test_evaluate_state_risk_structure():
    sample_input = {
        "state": "Test State",
        "anemia_women": 60,
        "female_education_years": 40
    }

    result = service.evaluate_state_risk(State(**sample_input))

    assert isinstance(result, dict)
    assert len(result.keys()) == 5
    assert "state" in result
    assert "anemia_women" in result
    assert "female_education_years" in result
    assert "risk" in result
    assert "reason" in result

def test_evaluate_state_risk_high_risk():
    sample_input = {
        "state": "Test State",
        "anemia_women": 60,
        "female_education_years": 5
    }

    result = service.evaluate_state_risk(State(**sample_input))
    assert result["risk"] == service.RiskLevel.HIGH

def test_evaluate_state_risk_moderate_anemia():
    sample_input = {
        "state": "Test State",
        "anemia_women": 60,
        "female_education_years": 7
    }

    result = service.evaluate_state_risk(State(**sample_input))
    assert result["risk"] == service.RiskLevel.MODERATE

def test_evaluate_state_risk_moderate_education():
    sample_input = {
        "state": "Test State",
        "anemia_women": 40,
        "female_education_years": 5
    }

    result = service.evaluate_state_risk(State(**sample_input))
    assert result["risk"] == service.RiskLevel.MODERATE

def test_evaluate_state_risk_low():
    sample_input = {
        "state": "Test State",
        "anemia_women": 40,
        "female_education_years": 8
    }

    result = service.evaluate_state_risk(State(**sample_input))
    assert result["risk"] == service.RiskLevel.LOW

def test_evaluate_state_risk_missing_data_both():
    sample_input = {
        "state": "Test State",
        "anemia_women": None,
        "female_education_years": None
    }
    result = service.evaluate_state_risk(State(**sample_input))
    assert result["risk"] == None


def test_evaluate_state_risk_missing_data_one():
    sample_input = {
        "state": "Test State",
        "anemia_women": None,
        "female_education_years": 5
    }
    result = service.evaluate_state_risk(State(**sample_input))
    assert result["risk"] == service.RiskLevel.MODERATE


# -------- calculate_risk_score --------
def test_calculate_risk_score_basic():
    sample_input = {
        "state": "Test State",
        "anemia_women": 50,
        "child_mortality_rate": 15,
        "bmi_low": 30
    }

    score = service.calculate_risk_score(State(**sample_input))

    assert isinstance(score, (int, float))
    assert score == pytest.approx(33.5, abs=0.01)

def test_calculate_risk_score_missing_data():
    sample_input = {
        "state": "Test State",
        "anemia_women": 50,
        "child_mortality_rate": None,
        "bmi_low": 30
    }

    score = service.calculate_risk_score(State(**sample_input))

    assert score == None

# -------- get_score_band --------
def test_get_score_band_low():
    score = 30
    band = service.get_score_band(score)

    assert band == service.RiskLevel.LOW

def test_get_score_band_missing_data():
    score = None
    band = service.get_score_band(score)

    assert band == None

def test_get_score_band_moderate():
    score = 50
    band = service.get_score_band(score)

    assert band == service.RiskLevel.MODERATE

def test_get_score_band_moderate_edge():
    score = 40
    band = service.get_score_band(score)

    assert band == service.RiskLevel.MODERATE

def test_get_score_band_high():
    score = 80
    band = service.get_score_band(score)

    assert band == service.RiskLevel.HIGH

def test_get_score_band_moderate_high_edge():
    score = 70
    band = service.get_score_band(score)

    assert band == service.RiskLevel.HIGH

# -------- get_top_n_states_by_risk_score --------
def test_top_n_states_basic():
    upload_data_for_testing(VALID_DATA_1)

    result = service.get_top_n_states_by_risk_score(n=3)

    assert len(result) == 3
    assert result[0]["risk_score"] >= result[1]["risk_score"]

def test_top_n_states_edge_zero():
    upload_data_for_testing(VALID_DATA_1)
    result = service.get_top_n_states_by_risk_score(n=0)

    assert len(result) == 1

def test_top_n_states_edge_greater_than_limit():
    upload_data_for_testing(VALID_DATA_1)
    result = service.get_top_n_states_by_risk_score(n=22)

    assert len(result) == 5

def test_top_n_states_order():
    upload_data_for_testing(VALID_DATA_1)
    result = service.get_top_n_states_by_risk_score(n=5)

    flag = False
    if result[0]["risk_score"] is None:
        flag = True
    for i in range(len(result) - 1):
        if not flag and result[i+1]["risk_score"] is None:
            flag = True
        if not flag:
            assert result[i]["risk_score"] >= result[i + 1]["risk_score"]
        else:
            assert result[i + 1]["risk_score"] is None

# -------- get_state_profile --------
def test_get_state_profile_structure():
    upload_data_for_testing(VALID_DATA_1)
    state_name = "B"
    result = service.get_state_profile_service(state_name)

    assert isinstance(result, dict)
    assert "state" in result
    assert "metrics" in result
    assert isinstance(result["metrics"], dict)
    assert "risk_score" in result
    assert "score_band" in result

def test_get_state_profile_metrics_structure():
    upload_data_for_testing(VALID_DATA_1)
    state_name = "B"
    result = service.get_state_profile_service(state_name)
    metrics = result["metrics"]
    assert "anemia_women" in metrics
    assert "bmi_low" in metrics
    assert "child_mortality_rate" in metrics
    assert "female_education_years" in metrics
    assert "rural_population" in metrics

# ------ data cleaning --------------
def test_drop_extra_columns():
    df = pd.DataFrame(EXTRA_COLUMN_DATA)
    
    clean_df = service.drop_extra_column(df)

    columns = set(clean_df.columns)
    required_columns = set(service.DemographicsServiceConstants.REQUIRED_COLUMNS)

    assert "unexpected_col" not in columns
    assert len(columns) == len(required_columns)
    assert len(required_columns - columns) == 0

def test_clean_state_column():
    df = pd.DataFrame(DIRTY_STATE_DATA)

    clean_df = service.clean_state_column(df)

    # There are 3/5 rows with dirty state name
    assert len(clean_df) == 2

def test_clean_numeric_columns():
#     DIRTY_NUMERIC_DATA = {
#     "state": ["A", "B", "C"],
#     "anemia_women": [50, "invalid", -10],
#     "bmi_low": [20, None, 40],
#     "child_mortality_rate": [10, "NaN", 5],
#     "female_education_years": [8, "text", 2],
#     "rural_population": [40, 30, 35]
# }
    df = pd.DataFrame(DIRTY_NUMERIC_DATA)
    numeric_cols = [
        "anemia_women", "bmi_low", "child_mortality_rate",
        "female_education_years", "rural_population"
    ]
    clean_df = service.clean_numeric_columns(df, numeric_cols)
    
    assert pd.isna(clean_df.loc[1, "anemia_women"])
    assert pd.isna(clean_df.loc[1, "bmi_low"])
    assert pd.isna(clean_df.loc[1, "child_mortality_rate"])
    assert pd.isna(clean_df.loc[1, "female_education_years"])
    
    assert pd.isna(clean_df.loc[2, "anemia_women"])