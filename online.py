from fastapi import FastAPI, Form, Path, Request
from fastapi.responses import HTMLResponse
from uvicorn import run
from searchengine import *
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from main import *


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def search(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/links", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("links.html", {"request": request})


@app.get("/results/{query}", response_class=HTMLResponse)
async def search_results(request: Request, query: str = Path(...)):
    results = []
    return templates.TemplateResponse(
        "results.html", {"request": request, "results": results, "query": query, "number": len(results)}
    )


def main():
    run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()