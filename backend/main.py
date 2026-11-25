
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from project1_blog import run_blog_crew

app = FastAPI(title="Neha's CrewAI Projects API")

# Allows her GitHub Pages website to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TopicInput(BaseModel):
    topic: str


@app.get("/")
def home():
    return {"message": "Neha's CrewAI backend is running"}


@app.post("/project1/blog")
def blog_post(data: TopicInput):
    try:
        result = run_blog_crew(data.topic)
        return {"project": "Blog Post Crew", "topic": data.topic, "result": result}
    except Exception as e:
        return {"error": str(e)}
