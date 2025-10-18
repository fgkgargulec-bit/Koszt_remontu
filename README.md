# Koszt remontu – instrukcja uruchomienia

## Wymagania
- Python 3.9 lub nowszy
- Połączenie z internetem (do instalacji zależności)
- Pakiet `streamlit` oraz lokalnie zainstalowany moduł `koszt_remontu`

## Szybki start (lokalnie na komputerze)
1. Otwórz terminal w katalogu projektu.
2. Utwórz i aktywuj wirtualne środowisko:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Zainstaluj wymagane pakiety:
   ```bash
   pip install streamlit
   pip install -e .
   ```
4. Uruchom aplikację:
   ```bash
   streamlit run app.py
   ```
5. Przeglądarka otworzy (lub zaproponuje otwarcie) adres `http://localhost:8501`, gdzie dostępny jest interfejs.

## Uruchomienie w GitHub Codespaces
1. W Codespaces otwórz nowy terminal (View → Terminal lub skrót ``Ctrl+` ``).
2. Sprawdź wersję Pythona (`python --version`). Jeśli środowisko jest świeże, utwórz i aktywuj wirtualne środowisko:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Zainstaluj zależności tak samo jak lokalnie:
   ```bash
   pip install streamlit
   pip install -e .
   ```
4. Uruchom Streamlit poleceniem dostosowanym do Codespaces:
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```
   *Nie trzeba tworzyć plików konfiguracyjnych ani wpisywać portu w oknie „Run and Debug”. Wystarczy terminal.*
5. Po chwili w prawym dolnym rogu pojawi się powiadomienie o wykrytym porcie 8501. Kliknij „Open in Browser” (lub wybierz port w panelu Ports i ustaw „Open in Browser”).
6. Interfejs Streamlit otworzy się w nowej karcie przeglądarki. Jeśli pojawi się monit o zaufanie dla połączenia, zaakceptuj go.
7. Aby zakończyć działanie aplikacji, w terminalu naciśnij `Ctrl+C`.

## Ręczne wywołania CLI
Jeżeli chcesz przetestować backend bez interfejsu, użyj poleceń:
```bash
python -m koszt_remontu.cli settings set-base "Adres bazy"
python -m koszt_remontu.cli settings set-travel-rate 2.5
python -m koszt_remontu.cli service add "Nazwa usługi" --unit sqm --rate 100
python -m koszt_remontu.cli quote --service "Nazwa usługi" --quantity 3 --client-address "Adres klienta"
```

Konfiguracja (baza, stawka, lista usług) zapisywana jest w pliku `.koszt_remontu_state.json` w katalogu domowym użytkownika.
