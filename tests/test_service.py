import pytest
from app import service

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


# -------- get_score_band --------
def test_get_score_band_low():
    score = 30
    band = service.get_score_band(score)

    assert band == service.RiskLevel.LOW

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

    result = service.get_top_n_states_by_risk_score(n=6)

    assert len(result) == 6
    assert result[0]["risk_score"] >= result[1]["risk_score"]

def test_top_n_states_edge_zero():
    result = service.get_top_n_states_by_risk_score(n=0)

    assert len(result) == 1

def test_top_n_states_edge_greater_than_limit():
    result = service.get_top_n_states_by_risk_score(n=22)

    assert len(result) <= 20

def test_top_n_states_order():
    result = service.get_top_n_states_by_risk_score(n=5)

    for i in range(len(result) - 1):
        assert result[i]["risk_score"] >= result[i + 1]["risk_score"]

# -------- get_state_profile --------
def test_get_state_profile_structure():
    state_name = "Tamil Nadu"
    result = service.get_state_profile_service(state_name)

    assert isinstance(result, dict)
    assert "state" in result
    assert "metrics" in result
    assert isinstance(result["metrics"], dict)
    assert "risk_score" in result
    assert "score_band" in result

def test_get_state_profile_metrics_structure():
    state_name = "Tamil Nadu"
    result = service.get_state_profile_service(state_name)
    metrics = result["metrics"]
    assert "anemia_women" in metrics
    assert "bmi_low" in metrics
    assert "child_mortality_rate" in metrics
    assert "female_education_years" in metrics
    assert "rural_population" in metrics