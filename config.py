import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent

load_dotenv(ROOT_DIR / ".env")

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

PROMPT_PATH = ROOT_DIR / os.getenv(
    "PROMPT_PATH", "prompts/v1_en.txt"
)

OUTPUT_SCHEMA_PATH = ROOT_DIR / "schemas" / "output.schema.json"

RESULTS_DIR = ROOT_DIR / os.getenv(
    "RESULTS_DIR", "results"
)
