
import json
import re
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator
from models import ParcelInput

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"

SCHEMA = json.loads(
    (ROOT / "schemas/input.schema.json").read_text(encoding="utf-8")
)
VALIDATOR = Draft202012Validator(SCHEMA)


def validate_case(data: dict) -> dict:
    result = ParcelInput.model_validate(data).model_dump()
    VALIDATOR.validate(result)
    return result


def save_case(data: dict, name: str) -> str:
    valid = validate_case(data)

    slug = unicodedata.normalize("NFKD", name)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug).strip("_").lower()[:80]

    if not slug:
        raise ValueError("Case name must not be empty.")

    CASES.mkdir(exist_ok=True)
    path = CASES / f"{slug}.json"

    number = 2
    while path.exists():
        path = CASES / f"{slug}_{number}.json"
        number += 1

    path.write_text(
        json.dumps(valid, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    return path.name


def list_cases() -> list[str]:
    return sorted(p.name for p in CASES.glob("*.json")) if CASES.exists() else []


def load_case(filename: str) -> dict:
    if filename not in list_cases():
        raise ValueError("Case file does not exist.")

    data = json.loads(
        (CASES / filename).read_text(encoding="utf-8")
    )
    return validate_case(data)
