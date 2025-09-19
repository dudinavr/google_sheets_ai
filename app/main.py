from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import gspread
from google.oauth2.service_account import Credentials
import uvicorn
from openai import OpenAI

from .llm import GoogleSheetAI
from .settings import settings

app = FastAPI()

google_creds = Credentials.from_service_account_file(
    "service_account_creds.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
gc = gspread.authorize(google_creds)

SHEET_ID = settings.SHEET_ID

templates = Jinja2Templates(directory="webui/templates")


class SheetData(BaseModel):
    values: list[list[str]]


@app.get("/sheet/{sheet_id}", response_model=SheetData)
def get_sheet(sheet_id: str):
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_values()
    return {"values": data}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask")
async def ask(question: str = Form(...), sheet_id: str = SHEET_ID):
    sheet_data = get_sheet(sheet_id).get('values')
    rows = sheet_data[1:]
    response = await GoogleSheetAI(api_key=settings.OPENAI_KEY, is_stream=False).answer_question(question, rows)
    return JSONResponse({"answer": response})


@app.post('/ask_stream')
async def ask_stream(question: str = Form(...), sheet_id: str = SHEET_ID):
    sheet_data = get_sheet(sheet_id).get('values')
    rows = sheet_data[1:]
    stream_response = GoogleSheetAI(api_key=settings.OPENAI_KEY, is_stream=True).stream_answer_question(question, rows)
    return StreamingResponse(stream_response, media_type="text/plain")


if __name__ == '__main__':
    uvicorn.run(app)