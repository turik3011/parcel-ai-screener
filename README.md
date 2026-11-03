# Parcel AI Screener

## Setup

**Requirements:** Python 3.10+ and an OpenAI API key.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Configure `.env`:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
PROMPT_PATH=prompts/Final_en.txt
```

A valid OpenAI API key with available API credits is required. The application runs locally and uses the **OpenAI API** for inference; no separate cloud deployment is needed.

## Run with Streamlit

```bash
streamlit run app.py
```

The application has two tabs:

- **Nová parcela:** Enter parcel information, validate it, and save the input as JSON.
- **Uložené parcely / analýza:** Select an existing parcel, run the LLM assessment, inspect the structured result, and download it as JSON.

Analysis results are saved locally and organized by prompt version.

## Run from the terminal

```bash
python analyzer.py --input cases/real_01_vranove_1289_2.json
```

To select a specific prompt:

```bash
python analyzer.py \
  --input cases/synthetic_03_injection.json \
  --prompt prompts/Final_en.txt
```

## Testing and evaluation

The project includes **8 test cases**:

- **4 real parcels** based on manually collected information from the Czech cadastral registry (ČÚZK).
- **4 synthetic cases** covering missing data, contradictory information, prompt injection, and easement/access interpretation.

Test cases can be analyzed individually through Streamlit or the terminal.

Expected results and evaluation criteria are available in `tests/expectations.json`. Model outputs can be compared manually against these criteria.

The prompt was improved iteratively, with earlier versions and their results retained for comparison.
