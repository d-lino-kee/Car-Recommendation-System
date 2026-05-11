from sqlalchemy import Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Car(Base):
    __tablename__ = "cars"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    make: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    body_style: Mapped[str] = mapped_column(String)
    price_usd: Mapped[float] = mapped_column(Float)

    reliability: Mapped[float] = mapped_column(Float)
    performance: Mapped[float] = mapped_column(Float)
    ergonomics: Mapped[float] = mapped_column(Float)
    ease_entry: Mapped[float] = mapped_column(Float)
    mpg: Mapped[float] = mapped_column(Float)
    drive: Mapped[str] = mapped_column(String)
    seat_height_cm: Mapped[float] = mapped_column(Float)
    cargo_l: Mapped[float] = mapped_column(Float)

    tag_outdoors: Mapped[bool] = mapped_column(Boolean)
    tag_city: Mapped[bool] = mapped_column(Boolean)
    tag_family: Mapped[bool] = mapped_column(Boolean)
    tag_track: Mapped[bool] = mapped_column(Boolean)
    tag_luxury: Mapped[bool] = mapped_column(Boolean)
    tag_economy: Mapped[bool] = mapped_column(Boolean)

    interactions: Mapped[list["Interaction"]] = relationship(back_populates = "car")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    # Optional auth fields could go here
    interactions: Mapped[list["Interaction"]] = relationship(back_populates = "user")

class Interaction(Base):
    __tablename__ = "interactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"))
    like: Mapped[bool] = mapped_column(Boolean)

    user: Mapped[User] = relationship(back_populates="interactions")
    car: Mapped[Car] = relationship(back_populates="interactions")