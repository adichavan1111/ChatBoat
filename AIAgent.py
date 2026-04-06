from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import csv, os
import openai

# Set your OpenAI API key
import os
from dotenv import load_dotenv
from langchain_openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve chat interface
@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(os.path.join("static", "index.html"))

# Submit patient info
@app.post("/submit")
def submit(name: str = Form(...), mobile: str = Form(...),
           address: str = Form(...), consultation: str = Form(...)):
    file_exists = os.path.isfile("patients.csv")
    with open("patients.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Mobile", "Address", "Consultation"])
        writer.writerow([name, mobile, address, consultation])
    return {"reply": f"Thanks {name}! Your {consultation} consultation request has been submitted. The doctor will contact you soon."}

# AI conversation endpoint
@app.post("/ask")
def ask_ai(message: str = Form(...)):
    try:
        # Call OpenAI GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful doctor assistant."},
                {"role": "user", "content": message}
            ],
            max_tokens=200
        )
        answer = response.choices[0].message.content
        return JSONResponse(content={"reply": answer})
    except Exception as e:
        return JSONResponse(content={"reply": f"AI error: {str(e)}"})