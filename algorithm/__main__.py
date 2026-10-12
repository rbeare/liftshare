import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print(data)