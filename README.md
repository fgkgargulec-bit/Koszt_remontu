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

### Pierwsze kroki w aplikacji
Po otwarciu interfejsu wykonaj kolejno:

1. W sekcji **Konfiguracja ustawień** wpisz adres bazy firmy oraz stawkę za kilometr i kliknij "Zapisz ustawienia".
2. W panelu **Usługi** dodaj oferowane pozycje. Z listy wybierz jednostkę (nazwy w języku polskim są mapowane na wymagane przez CLI skróty).
3. W formularzu **Wyceń usługę** uzupełnij nazwę usługi, ilość, adres klienta oraz – jeśli to potrzebne – dodatkowe dane w formacie JSON.

Po wysłaniu formularzy aplikacja pokazuje wynik działania CLI (treść odpowiedzi oraz kod powrotu), dzięki czemu łatwo sprawdzić, czy operacja zakończyła się sukcesem.

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
5. Po chwili w prawym dolnym rogu pojawi się powiadomienie o wykrytym porcie 8501. Kliknij „Open in Browser” **lub** otwórz zakładkę *Ports*, znajdź pozycję `8501` i wybierz akcję *Open in Browser*. Upewnij się, że numer portu to dokładnie **8501** (nie `508501` ani inna wartość).
6. Interfejs Streamlit otworzy się w nowej karcie przeglądarki. Jeśli pojawi się monit o zaufanie dla połączenia, zaakceptuj go.
7. Aby zakończyć działanie aplikacji, w terminalu naciśnij `Ctrl+C`.

### Rozwiązywanie problemów w Codespaces
- **Błąd 404 po kliknięciu ikony globusa** – oznacza, że port 8501 nie jest aktualnie obsługiwany. Sprawdź, czy w terminalu nadal działa polecenie `streamlit run …` i nie zakończyło się błędem. Jeśli proces został przerwany, uruchom go ponownie tym samym poleceniem.
- **Komunikat „Strona nie działa” (502/504)** – upewnij się, że otwierasz właściwy port `8501`. Najbezpieczniej skopiować adres *External URL* z terminala (np. `https://<identyfikator>-8501.app.github.dev`) lub kliknąć akcję *Open in Browser* w zakładce *Ports*. Jeśli port był ustawiony jako prywatny, zmień jego widoczność na *Public*.
- **Brak portu 8501 w zakładce Ports** – otwórz zakładkę *Ports* (dolny panel), znajdź wpis `8501` i ustaw akcję *Open in Browser*. Jeżeli port nie pojawia się na liście, upewnij się, że Streamlit wystartował poprawnie – w terminalu powinny pojawić się adresy URL, np. `External URL: https://...githubpreview.dev`.
- **Komunikat o brakującym pakiecie `streamlit`** – oznacza, że instalacja zależności się nie powiodła. Wykonaj ponownie `pip install streamlit` (w aktywowanym środowisku wirtualnym). Jeśli środowisko nie ma dostępu do internetu, skorzystaj z obrazu Codespaces, który ma Streamlit wbudowany, albo poproś administratora o włączenie dostępu.

## Ręczne wywołania CLI
Jeżeli chcesz przetestować backend bez interfejsu, użyj poleceń:
```bash
python -m koszt_remontu.cli settings set-base "Adres bazy"
python -m koszt_remontu.cli settings set-travel-rate 2.5
python -m koszt_remontu.cli service add "Nazwa usługi" --unit sqm --rate 100
python -m koszt_remontu.cli quote --service "Nazwa usługi" --quantity 3 --client-address "Adres klienta"
# alias: python -m koszt_remontu.cli price --service "Nazwa usługi" --quantity 3 --client-address "Adres klienta"
```

Konfiguracja (baza, stawka, lista usług) zapisywana jest w pliku `.koszt_remontu_settings.json` w katalogu domowym użytkownika.
