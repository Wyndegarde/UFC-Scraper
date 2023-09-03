from fastapi import FastAPI
from ufc_scraper.pipelines import NextEventPipeline

app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

@app.get("/")
def read_root():
    next_event = NextEventPipeline()
    all_info = next_event.scrape_next_event()
    return all_info