from fastapi import FastAPI, Form, Path, Request
from fastapi.responses import HTMLResponse
from uvicorn import run
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from searchengine import SearchEngine
from utilities import *
import locale
import re


app = FastAPI()
locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
file = "./code_du_travail.csv"
dataset = read_csv(file)
index = "./index_cdt.pkl"
engine = SearchEngine(dataset=dataset, index_path=index)


def solve_query(query):
    """
    Tries to solve the user's query using a combination of tools
    Parameters:
        query (str): the string of characters the user queried
    Returns:
        The "search engine's" result
    """
    results = []
    search_results = engine.search(query)
    for article, score in search_results.items():
        article = dataset[dataset['article_id']==article]
        if not article.empty:
            results.append(article)
        if len(results) > 5:
            break
    return results


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
    results = solve_query(query)
    for result in results:
        result['date_deb'].iloc[0] = convert_date(result['date_deb'].iloc[0])
        result['texte'].iloc[0] = result['texte'].iloc[0].replace("<p>", "").replace("</p>", "\n").replace("<br/>", "\n")
        result['texte'].iloc[0] = re.sub('<.*?>', '', result['texte'].iloc[0])
        result['texte'].iloc[0] = result['texte'].iloc[0].split("\n")
    return templates.TemplateResponse(
        "results.html", {"request": request, "results": results, "query": query, "number": len(results)}
    )


def main():
    run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()