from app.service import validate_and_upload_df
import pandas as pd

VALID_DATA_1 = {
    "state": ["A", "B", "C", "D", "E"],
    "anemia_women": [50, 60, 70, 80, 55],
    "bmi_low": [20, 30, 25, 35, 22],
    "child_mortality_rate": [10, 20, 15, 25, 12],
    "female_education_years": [8, 10, 12, 6, 9],
    "rural_population": [40, 50, 60, 30, 45]
}

VALID_DATA_2 = {
    "state": ["A", "B", "C", "D", "E", "F"],
    "anemia_women": [50, 60, 70, 80, 55, 66],
    "bmi_low": [20, 30, 25, 35, 22, 33],
    "child_mortality_rate": [10, 20, 15, 25, 12, 22],
    "female_education_years": [8, 10, 12, 6, 9, 10],
    "rural_population": [40, 50, 60, 30, 45, 55]
}

MISSING_DATA_1 = {
    "state": ["A", "B", None, "D"],
    "anemia_women": [50, None, 70, 80],
    "bmi_low": [20, 30, None, 35],
    "child_mortality_rate": [10, None, 15, 25],
    "female_education_years": [8, 10, None, 6],
    "rural_population": [40, None, 60, 30]
}

DIRTY_STATE_DATA = {
    "state": ["A", "", "nan", None, "E"],
    "anemia_women": [50, 60, 70, 80, 55],
    "bmi_low": [20, 30, 25, 35, 22],
    "child_mortality_rate": [10, 20, 15, 25, 12],
    "female_education_years": [8, 10, 12, 6, 9],
    "rural_population": [40, 50, 60, 30, 45]
}

DIRTY_NUMERIC_DATA = {
    "state": ["A", "B", "C"],
    "anemia_women": [50, "invalid", -10],
    "bmi_low": [20, None, 40],
    "child_mortality_rate": [10, "NaN", 5],
    "female_education_years": [8, "text", 2],
    "rural_population": [40, 30, 35]
}

EXTRA_COLUMN_DATA = {
    "state": ["A", "B"],
    "anemia_women": [50, 60],
    "bmi_low": [20, 30],
    "child_mortality_rate": [10, 20],
    "female_education_years": [8, 10],
    "rural_population": [40, 50],
    "unexpected_col": [999, 999]
}

SMALL_DATA_1 = {
    "state": ["A"],
    "anemia_women": [50],
    "bmi_low": [20],
    "child_mortality_rate": [10],
    "female_education_years": [8],
    "rural_population": [40]
}

def upload_data_for_testing(data):

    df = pd.DataFrame(data)
    return validate_and_upload_df(df)