from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from sqlalchemy.orm import Session
from .models import Car, Interaction

auto_num_features = [
    "reliability", "performance", "ergonomics", "ease_entry", "mpg",
    "seat_height_cm", "cargo_l",
]

lifestyle_tags = [
    "tag_outdoors", "tag_city", "tag_family", "tag_track", "tag_luxury", "tag_economy",
]


def car_matrix(cars: list[Car]) -> np.ndarray:
    X = []
    for c in cars:
        row = [getattr(c, f) for f in auto_num_features]
        row += [int(getattr(c, t)) for t in lifestyle_tags]
        X.append(row)
    X = np.asarray(X, dtype=float)
    if X.size:
        num = X[:, :len(auto_num_features)]
        X[:, :len(auto_num_features)] = (num - num.min(axis=0)) / np.maximum(1e-9, num.ptp(axis=0))
    return X


def user_pref_vector(req: dict) -> np.ndarray:
    prefs = np.array([
        req.get("reliability", 5),
        req.get("performance", 5),
        req.get("ergonomics", 5),
        req.get("ease_entry", 5),
        5,  # mpg neutral
        5,  # seat height neutral
        5,  # cargo neutral
    ], dtype=float) / 10.0

    tags = np.array([
        1.0 if req.get("lifestyle_outdoors") else 0.0,
        1.0 if req.get("lifestyle_city") else 0.0,
        1.0 if req.get("lifestyle_family") else 0.0,
        1.0 if req.get("lifestyle_track") else 0.0,
        1.0 if req.get("lifestyle_luxury") else 0.0,
        1.0 if req.get("lifestyle_economy") else 0.0,
    ])
    return np.concatenate([prefs, tags])


def content_scores(X: np.ndarray, u: np.ndarray) -> np.ndarray:
    if X.size == 0:
        return np.array([])
    u = u / (np.linalg.norm(u) + 1e-9)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    return Xn @ u


def train_user_model(db: Session, user_id: int, cars: list[Car]) -> LogisticRegression | None:
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    if len(interactions) < 6:
        return None
    id_to_car = {c.id: c for c in cars}
    usable = [ix for ix in interactions if ix.car_id in id_to_car]
    if len(usable) < 6:
        return None

    X_list, y_list = [], []
    for ix in usable:
        c = id_to_car[ix.car_id]
        row = [getattr(c, f) for f in auto_num_features]
        row += [int(getattr(c, t)) for t in lifestyle_tags]
        X_list.append(row)
        y_list.append(1 if ix.like else 0)

    if len(set(y_list)) < 2:
        return None  # logistic regression needs both classes

    X = np.asarray(X_list, dtype=float)
    num = X[:, :len(auto_num_features)]
    X[:, :len(auto_num_features)] = (num - num.min(axis=0)) / np.maximum(1e-9, num.ptp(axis=0))
    y = np.asarray(y_list, dtype=int)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, y)
    return clf


def hybrid_rank(db: Session, req: dict, cars: list[Car]):
    X = car_matrix(cars)
    u = user_pref_vector(req)
    cs = content_scores(X, u)

    ps = None
    user_id = req.get("user_id")
    if user_id is not None:
        model = train_user_model(db, user_id, cars)
        if model is not None:
            ps = model.predict_proba(X)[:, 1]

    final = cs if ps is None else 0.6 * cs + 0.4 * ps
    order = np.argsort(-final)
    return order, final
