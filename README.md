# Full-Stack Health Risk Analytics System

A backend analytics system built using **FastAPI** and **PostgreSQL** to process structured demographic data and generate risk-based insights via REST APIs.

## 🚀 Features

* Data pipeline with **staging → main tables** for clean and reliable data handling
* Rule-based scoring system to compute **risk scores** and categorize records into bands
* REST APIs for:

  * State-level summaries
  * Top-ranked states by score
  * State-wise detailed profiles
* Environment-based configuration for secure and flexible deployments
* Deployed backend with live API documentation

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Database:** PostgreSQL
* **ORM / DB Layer:** SQLAlchemy
* **Deployment:** Render

## 📦 Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── service.py
└── requirements.txt
```

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sairam-M/nfhs-analytics/main
cd nfhs-analytics
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=<your_postgres_connection_string>
```

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

## 📡 API Endpoints

* `GET /risk-scores` → Fetch computed risk scores
* `GET /top-states-by-score` → Get ranked list of states
* `GET /state-profile/{state}` → Get detailed metrics for a specific state
* `GET /demograohics` → Fetch all states
* `GET /states` → Fetch state list
* `GET /high-risk-states` → Fetch High risk states
* `POST /upload` → Upload CSV file to DB

## 🌐 Deployment

* Hosted on Render
* API documentation available at:
  👉 `https://nfhs-analytics.onrender.com/docs`

## 📌 Key Concepts Demonstrated

* Backend API design
* Database modeling and querying
* Data pipeline design (staging → production tables)
* Rule-based analytics and scoring logic
* Cloud deployment with environment configuration

## 📄 License

This project is open-source and available for learning and extension.

---
