# src/frameweb/web/main.py
from fastapi import FastAPI

app = FastAPI()  # <-- The variable name must be 'app'


@app.get("/")
def read_root():
    return {"Hello": "World again"}
