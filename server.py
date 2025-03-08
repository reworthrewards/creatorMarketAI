from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def run_streamlit():
    """Ejecuta Streamlit en segundo plano"""
    subprocess.Popen(["streamlit", "run", "index.py"])
    return {"message": "Streamlit app is running"}