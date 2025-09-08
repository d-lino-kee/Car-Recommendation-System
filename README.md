# Car Recommender ML (FastAPI + SQLite + scikit-learn)

Lifestyle-driven car recommendations. Users share priorities — reliability, performance, ergonomics, ease of entry — plus hobbies. The system blends a content-based score with a learned model that adapts to feedback (like/dislike), giving personalized results.

## Features
- 🧠 Hybrid recommender: weighted cosine/content score + per-user logistic regression when enough feedback exists.
- 🗃️ SQLite via SQLAlchemy (cars, users, interactions).
- 🌐 FastAPI with Jinja2 templates (no JS build step required).
- 📦 Simple dataset with 20 example cars; easy to extend.
- 🔁 Feedback loop: like/dislike refines future suggestions.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
