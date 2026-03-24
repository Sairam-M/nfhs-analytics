# Connect with Postgres SQL Database using SQLAlchemy
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Sql123@localhost/nfhs_db"
engine = create_engine(DATABASE_URL)

def get_demographics_data():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM demographics"))
        return result.fetchall()

# Create __main__ block to test the connection
if __name__ == "__main__":
    data = get_demographics_data()
    print(type(data))
    print(data)