from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "NFHS Analytics API is running!"}