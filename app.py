
import json

import streamlit as st
from jsonschema import ValidationError as SchemaError
from pydantic import ValidationError as ModelError

from storage import list_cases, load_case, save_case


def parse_lines(text: str, verified: bool) -> list[str] | None:
    values = [line.strip() for line in text.splitlines() if line.strip()]
    if not verified and values:
        raise ValueError("Označte seznam jako ověřený, pokud obsahuje položky.")
    return values if verified else None


st.set_page_config(page_title="Viagem – Parcely")
st.title("Viagem – Parcel Assessment")

create_tab, analysis_tab = st.tabs([
    "Nová parcela",
    "Uložené parcely / analýza"
])

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

        protection_checked = st.checkbox("Ochranné režimy ověřeny")
        protection = st.text_area("Způsoby ochrany – jeden na řádek")

        encumbrance_checked = st.checkbox(
            "Omezení vlastnického práva ověřena"
        )
        encumbrances = st.text_area("Omezení – jedno na řádek")

        context = st.text_area(
            "Doplňující ověřené informace (nepovinné)"
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
                    protection, protection_checked
                ),
                "registered_encumbrances": parse_lines(
                    encumbrances, encumbrance_checked
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


with analysis_tab:
    files = list_cases()

    if not files:
        st.info("Zatím nejsou uloženy žádné parcely.")
    else:
        selected = st.selectbox("Vyberte uložený případ", files)
        data = load_case(selected)

        st.json(data)

        st.download_button(
            "Stáhnout JSON",
            json.dumps(data, ensure_ascii=False, indent=2),
            file_name=selected,
            mime="application/json"
        )

        st.info(
            "V dalším kroku sem připojíme analýzu pomocí LLM."
        )
