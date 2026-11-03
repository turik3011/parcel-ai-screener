
import json

import streamlit as st
from jsonschema import ValidationError as SchemaError
from pydantic import ValidationError as ModelError

from analyzer import analyze_parcel
from config import MODEL_NAME, PROMPT_PATH, RESULTS_DIR, ROOT_DIR
from storage import list_cases, load_case, save_case


def parse_lines(text: str, verified: bool) -> list[str] | None:
    values = [line.strip() for line in text.splitlines() if line.strip()]

    if not verified and values:
        raise ValueError(
            "Mark the list as verified if it contains entries."
        )

    return values if verified else None


st.set_page_config(page_title="Viagem – Parcely")
st.title("Viagem – Parcel Assessment")

create_tab, analysis_tab = st.tabs([
    "Nová parcela",
    "Uložené parcely / analýza"
])


# Parcel creation
with create_tab:
    with st.form("parcel"):
        name = st.text_input(
            "Název případu",
            placeholder="real_01_vranove"
        )

        cadastral_area = st.text_input("Katastrální území *")
        parcel_number = st.text_input("Parcelní číslo *")
        area = st.text_input("Výměra v m² *")
        land_type = st.text_input("Druh pozemku *")
        land_use = st.text_input("Způsob využití (nepovinné)")

        protection_checked = st.checkbox(
            "Ochranné režimy ověřeny"
        )
        protection = st.text_area(
            "Způsoby ochrany – jeden na řádek"
        )

        encumbrance_checked = st.checkbox(
            "Omezení vlastnického práva ověřena"
        )
        encumbrances = st.text_area(
            "Omezení – jedno na řádek"
        )

        context = st.text_area(
            "Doplňující informace (nepovinné)"
        )

        submitted = st.form_submit_button(
            "Uložit input JSON",
            type="primary"
        )

    if submitted:
        try:
            data = {
                "cadastral_area": cadastral_area,
                "parcel_number": parcel_number,
                "area_m2": int(area),
                "land_type": land_type,
                "land_use": land_use.strip() or None,
                "protection_regimes": parse_lines(
                    protection,
                    protection_checked
                ),
                "registered_encumbrances": parse_lines(
                    encumbrances,
                    encumbrance_checked
                ),
                "additional_context": context.strip() or None,
            }

            filename = save_case(
                data,
                name or f"{cadastral_area}_{parcel_number}"
            )

            st.success(f"Uloženo: cases/{filename}")

        except (ValueError, ModelError, SchemaError) as exc:
            st.error(f"Neplatná data: {exc}")


# Saved parcels and LLM analysis
with analysis_tab:
    files = list_cases()

    if not files:
        st.info("Zatím nejsou uloženy žádné parcely.")

    else:
        selected = st.selectbox(
            "Vyberte uložený případ",
            files
        )

        data = load_case(selected)

        st.subheader("Vstupní data")
        st.json(data)

        st.download_button(
            "Stáhnout vstupní JSON",
            data=json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            file_name=selected,
            mime="application/json"
        )

        st.divider()

        st.subheader("Analýza pomocí LLM")
        st.caption(
            f"Model: {MODEL_NAME} | Prompt: {PROMPT_PATH.name}"
        )

        result_dir = RESULTS_DIR / PROMPT_PATH.stem
        result_path = result_dir / selected

        if st.button(
            "Analyzovat parcelu",
            type="primary"
        ):
            try:
                with st.spinner("Probíhá analýza..."):
                    result = analyze_parcel(
                        input_path=ROOT_DIR / "cases" / selected,
                        prompt_path=PROMPT_PATH,
                        model=MODEL_NAME
                    )

                    result_dir.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    result_path.write_text(
                        json.dumps(
                            result,
                            ensure_ascii=False,
                            indent=2
                        ) + "\n",
                        encoding="utf-8"
                    )

                st.success(
                    "Analýza byla úspěšně dokončena."
                )

            except Exception as exc:
                st.error(f"Analýza se nezdařila: {exc}")

        if result_path.exists():
            st.divider()
            st.subheader("Výsledek analýzy")

            result_data = json.loads(
                result_path.read_text(encoding="utf-8")
            )

            st.json(result_data)

            st.download_button(
                "Stáhnout výsledek JSON",
                data=json.dumps(
                    result_data,
                    ensure_ascii=False,
                    indent=2
                ),
                file_name=selected,
                mime="application/json"
            )
