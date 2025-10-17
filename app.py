"""Simple interface for the Koszt Remontu CLI."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import streamlit as st

# Paths used for persisting app state. This keeps the interface functional even
# when the CLI is executed multiple times within the same Streamlit session.
STATE_PATH = Path(".koszt_remontu_state.json")


@dataclass
class CommandResult:
    """Container for subprocess execution results."""

    stdout: str
    stderr: str
    returncode: int

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _run_cli(cmd: list[str], payload: Optional[str] = None) -> CommandResult:
    """Execute the Koszt Remontu CLI and capture its output."""

    completed = subprocess.run(
        cmd,
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandResult(
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )


def _load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text("utf-8"))
    return {"base": "", "travel_rate": ""}


def _save_state(base: str, travel_rate: str) -> None:
    STATE_PATH.write_text(json.dumps({"base": base, "travel_rate": travel_rate}))


state = _load_state()
st.set_page_config(page_title="Koszt remontu")
st.title("Koszt remontu")

with st.expander("Konfiguracja ustawień", expanded=False):
    with st.form("settings_form"):
        base_value = st.text_input("Baza", value=state.get("base", ""))
        travel_rate_value = st.text_input(
            "Stawka za dojazd (PLN/km)", value=state.get("travel_rate", "")
        )
        submitted_settings = st.form_submit_button("Zapisz ustawienia")

    if submitted_settings:
        if base_value:
            base_cmd = [
                "python",
                "-m",
                "koszt_remontu.cli",
                "settings",
                "set-base",
                base_value,
            ]
            base_result = _run_cli(base_cmd)
            if base_result.ok:
                st.success("Ustawiono bazę")
            else:
                st.error(base_result.stderr or "Nie udało się ustawić bazy")
        if travel_rate_value:
            travel_cmd = [
                "python",
                "-m",
                "koszt_remontu.cli",
                "settings",
                "set-travel-rate",
                travel_rate_value,
            ]
            travel_result = _run_cli(travel_cmd)
            if travel_result.ok:
                st.success("Ustawiono stawkę dojazdu")
            else:
                st.error(
                    travel_result.stderr or "Nie udało się ustawić stawki dojazdu"
                )
        _save_state(base_value, travel_rate_value)


st.header("Wyceń usługę")
with st.form("quote_form"):
    q_name = st.text_input("Usługa")
    qty = st.number_input("Ilość", min_value=1, step=1)
    client_address = st.text_input("Adres klienta")
    json_payload = st.text_area(
        "Dodatkowe dane w formacie JSON (opcjonalnie)",
        value="",
        placeholder="{}",
    )
    submit_quote = st.form_submit_button("Wyceń")

if submit_quote:
    cmd = [
        "python",
        "-m",
        "koszt_remontu.cli",
        "quote",
        "--service",
        q_name,
        "--quantity",
        str(qty),
        "--client-address",
        client_address,
    ]

    payload: Optional[str] = json_payload.strip() or None
    if payload:
        try:
            json.loads(payload)
        except json.JSONDecodeError:
            st.error("Niepoprawny JSON w dodatkowych danych")
        else:
            result = _run_cli(cmd, payload=payload)
    else:
        result = _run_cli(cmd)

    if result.ok:
        st.code(result.stdout or "", language="json")
        st.success("Polecenie zakończyło się powodzeniem")
    else:
        if result.stderr:
            st.error(result.stderr)
        st.warning(f"Polecenie zwróciło kod {result.returncode}")
