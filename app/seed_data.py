import csv
from pathlib import Path

from .database import SessionLocal
from .models import Car

CSV_PATH = Path("Data/cars.csv")

def _to_bool(value: str) -> bool:
    return str(value).strip() in {"1", "true", "yes", "y"}

def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Car).count() > 0:
            return
        if not CSV_PATH.exists():
            return
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Car(
                    make=row["make"],
                    model=row["model"],
                    year=int(row["year"]),
                    body_style=row["body_style"],
                    price_usd=float(row["price_usd"]),
                    reliability=float(row["reliability"]),
                    performance=float(row["performance"]),
                    ergonomics=float(row["ergonomics"]),
                    ease_entry=float(row["ease_entry"]),
                    mpg=float(row["mpg"]),
                    drive=row["drive"],
                    seat_height_cm=float(row["seat_height_cm"]),
                    cargo_l=float(row["cargo_l"]),
                    tag_outdoors=_to_bool(row["tag_outdoors"]),
                    tag_city=_to_bool(row["tag_city"]),
                    tag_family=_to_bool(row["tag_family"]),
                    tag_track=_to_bool(row["tag_track"]),
                    tag_luxury=_to_bool(row["tag_luxury"]),
                    tag_economy=_to_bool(row["tag_economy"]),
                ))
        db.commit()
    finally:
        db.close()
