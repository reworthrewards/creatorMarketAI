from fastapi import FastAPI
import subprocess
import time

app = FastAPI()

@app.get("/")
def run_streamlit():
    try:
        process = subprocess.Popen(["streamlit", "run", "index.py"])
        time.sleep(2)  # Da tiempo para iniciar
        return {"message": "Streamlit app is running"}
    except Exception as e:
        return {"error": str(e)}