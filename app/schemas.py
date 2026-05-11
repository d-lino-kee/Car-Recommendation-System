from pydantic import BaseModel
from typing import Optional

class RecommendRequest(BaseModel):
    reliability: int
    performance: int
    ergonomics: int
    ease_entry: int
    lifestyle_outdoors: bool
    lifestyle_city: bool
    lifestyle_family: bool
    lifestyle_track: bool
    lifestyle_luxury: bool
    lifestyle_economy: bool
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    user_id: Optional[int] = None

class CarOut(BaseModel):
    id: int
    name: str
    year: int
    body_style: str
    price_usd: float
    score: float
    class Config:
        from_attributes = True

class Feedback(BaseModel):
    user_id: int
    car_id: int
    like: bool