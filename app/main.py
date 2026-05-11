from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from .database import Base, engine, get_session
from .models import Car, User, Interaction
from .schemas import Feedback
from .recommender import hybrid_rank
from . import seed_data

app = FastAPI(title = "Car Recommender ML")
app.mount("/static", StaticFiles(directory = "app/static"), name = "static")
templates = Jinja2Templates(directory="app/templates")

# Ensure DB tables exist and seed if empty
Base.metadata.create_all(bind=engine)
seed_data.seed()

def db_dep():
    with get_session() as db:
        yield db

@app.get("/", response_class = HTMLResponse)
async def index(request: Request, db: Session = Depends(db_dep)):
    # ensure an anonymous user exists
    user = db.query(User).first()
    if not user:
        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)
    return templates.TemplateResponse(request, "index.html", {"user_id": user.id})

@app.post("/recommend", response_class = HTMLResponse)
async def recommend(
    request: Request,
    reliability: int = Form(...),
    performance: int = Form(...),
    ergonomics: int = Form(...),
    ease_entry: int = Form(...),
    lifestyle_outdoors: Optional[bool] = Form(False),
    lifestyle_city: Optional[bool] = Form(False),
    lifestyle_family: Optional[bool] = Form(False),
    lifestyle_track: Optional[bool] = Form(False),
    lifestyle_luxury: Optional[bool] = Form(False),
    lifestyle_economy: Optional[bool] = Form(False),
    price_min: Optional[int] = Form(None),
    price_max: Optional[int] = Form(None),
    user_id: Optional[int] = Form(None),
    db: Session = Depends(db_dep),
):
    # Build request dict
    req = dict(
        reliability=reliability,
        performance=performance,
        ergonomics=ergonomics,
        ease_entry=ease_entry,
        lifestyle_outdoors=bool(lifestyle_outdoors),
        lifestyle_city=bool(lifestyle_city),
        lifestyle_family=bool(lifestyle_family),
        lifestyle_track=bool(lifestyle_track),
        lifestyle_luxury=bool(lifestyle_luxury),
        lifestyle_economy=bool(lifestyle_economy),
        user_id=int(user_id) if user_id else None,
    )

    cars = db.query(Car).all()
    # price filter
    if price_min is not None:
        cars = [c for c in cars if c.price_usd >= price_min]
    if price_max is not None:
        cars = [c for c in cars if c.price_usd <= price_max]

    order, scores = hybrid_rank(db, req, cars)
    ranked = []
    for idx in order[:10]:
        c = cars[idx]
        ranked.append({
            "id": c.id,
            "name": f"{c.make} {c.model}",
            "year": c.year,
            "body_style": c.body_style,
            "price_usd": c.price_usd,
            "score": round(float(scores[idx]), 4)
        })

    return templates.TemplateResponse(request, "results.html", {"results": ranked, "user_id": user_id})


@app.post("/feedback")
async def feedback(fb: Feedback, db: Session = Depends(db_dep)):
    # ensure user exists
    user = db.query(User).get(fb.user_id)
    if not user:
        user = User(id = fb.user_id)
        db.add(user)
        db.commit()
    inter = Interaction(user_id = fb.user_id, car_id = fb.car_id, like = fb.like)
    db.add(inter)
    db.commit()
    return {"status": "ok"}

@app.get("/api/cars")
async def list_cars(db: Session = Depends(db_dep)):
    cars = db.query(Car).all()
    return [
        {
            "id": c.id,
            "name": f"{c.make} {c.model}",
            "year": c.year,
            "price_usd": c.price_usd,
        }
        for c in cars
    ]