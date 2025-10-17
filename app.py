import subprocess
import json
import streamlit as st

st.set_page_config(page_title="Koszt remontu", page_icon="🧱", layout="centered")
st.title("🧱 Koszt remontu – demo w przeglądarce")
st.caption("Cienkie UI nad istniejącym CLI. Nie zmienia logiki aplikacji.")

st.subheader("1) Dodaj / podejrzyj usługę")
with st.form("add_service"):
    name = st.text_input("Nazwa usługi", "Układanie płytek")
    unit = st.text_input("Jednostka (np. sqm, h)", "sqm")
    rate = st.number_input("Stawka za jednostkę", min_value=0.0, value=120.0, step=1.0)
    submitted = st.form_submit_button("Zapisz usługę")
    if submitted:
        cmd = [
            "python", "-m", "koszt_remontu.cli", "service", "add",
            "--name", name, "--unit", unit, "--rate", str(rate)
        ]
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode == 0:
            st.success("Usługa zapisana.")
        else:
            st.error(out.stderr or "Błąd przy zapisie usługi.")

st.divider()
st.subheader("2) Oblicz wycenę")
col1, col2 = st.columns(2)
with col1:
    q_name = st.text_input("Usługa do wyceny", "Układanie płytek", key="q_name")
    qty = st.number_input("Ilość (w jednostkach usługi)", min_value=0.0, value=10.0, step=1.0)
with col2:
    distance = st.number_input("Dystans dojazdu [km]", min_value=0.0, value=25.0, step=1.0)
    base_addr = st.text_input("Adres bazowy (opcjonalnie)", "Gdynia")

if st.button("Policz"):
    cmd = [
        "python", "-m", "koszt_remontu.cli", "price",
        "--service", q_name,
        "--qty", str(qty),
        "--distance", str(distance)
    ]
    if base_addr:
        cmd += ["--base", base_addr]

    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode == 0:
        txt = out.stdout.strip()
        try:
            data = json.loads(txt)
            st.success("Wycena policzona.")
            st.json(data)
        except json.JSONDecodeError:
            st.success("Wycena policzona.")
            st.code(txt)
    else:
        st.error(out.stderr or "Błąd podczas liczenia.")
