from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse
from transcribe import transcribe, saveData, generate_html
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/")
# def index():
#     index = ""
#
#     return HTMLResponse(index)


@app.get("/api/")
def api(url: str, start_time=None, end_time=None, max_symbols=None):
    data = transcribe(url, start_time, end_time, max_symbols)
    return {
        "url": url,
        "data": data
    }


@app.post("/api/")
def update_article(url: str, article):
    saveData(url, article)
    return {"message": 'Success'}


@app.get("/api/gen_html/")
def gen_html(url: str):
    file_path = generate_html(url)
    return FileResponse(file_path, media_type="text/html")