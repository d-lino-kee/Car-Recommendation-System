import json, re, urllib.parse, urllib.request

BASE = "http://127.0.0.1:8000"


def get(path):
    return urllib.request.urlopen(BASE + path).read().decode()


def post_form(path, fields):
    data = urllib.parse.urlencode(fields).encode()
    return urllib.request.urlopen(BASE + path, data=data).read().decode()


def post_json(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(req).read().decode()


print("[1] GET /          ", "ok" if "Your preferences" in get("/") else "FAIL")
cars = json.loads(get("/api/cars"))
print(f"[2] GET /api/cars   {len(cars)} cars seeded")

html = post_form("/recommend", {
    "reliability": 8, "performance": 5, "ergonomics": 7, "ease_entry": 8,
    "lifestyle_family": "on", "lifestyle_economy": "on",
})
names = re.findall(r'<div class="name">([^<]+)</div>', html)
print(f"[3] POST /recommend top 3: {names[:3]}")

print("[4] POST /feedback ", post_json("/feedback", {"user_id": 1, "car_id": cars[0]["id"], "like": True}))
