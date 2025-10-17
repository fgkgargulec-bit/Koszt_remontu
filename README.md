# Koszt remontu

Aplikacja konsolowa służąca do wyceny usług remontowych z uwzględnieniem kosztu dojazdu. Pozwala wykonawcy definiować usługi, ustawiać stawkę za kilometr oraz adres bazowy, a klientowi szybko policzyć wycenę dla konkretnego zlecenia.

## Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Użycie

Po instalacji można korzystać z polecenia:

```bash
python -m koszt_remontu.cli <polecenie>
```

### Definiowanie usług

Dodanie nowej usługi rozliczanej za metr kwadratowy:

```bash
python -m koszt_remontu.cli service add "Układanie płytek" --unit sqm --rate 120
```

Dostępne jednostki to `sqm` (metry kwadratowe), `hour` (godzina) oraz `item` (pozycja).

Wyświetlenie zdefiniowanych usług:

```bash
python -m koszt_remontu.cli service list
```

### Konfiguracja ustawień wykonawcy

Ustawienie adresu bazowego, od którego liczony jest dojazd, oraz stawki za kilometr:

```bash
python -m koszt_remontu.cli settings set-base "Rynek Główny 1, Kraków"
python -m koszt_remontu.cli settings set-travel-rate 2.5
```

Adres bazowy oraz stawka zapisywane są w pliku konfiguracyjnym użytkownika (`~/.koszt_remontu/data.json`).

### Kalkulacja wyceny

```bash
python -m koszt_remontu.cli quote --service "Układanie płytek" --quantity 35 --client-address "ul. Marszałkowska 1, Warszawa"
```

Polecenie korzysta z usługi geokodowania OpenStreetMap (Nominatim) do przeliczenia adresów na współrzędne i oblicza odległość w kilometrach. Do wyniku dodawany jest koszt robocizny oraz koszt przejazdu zgodnie z ustawioną stawką.

> **Uwaga:** W środowiskach bez dostępu do Internetu geokodowanie adresów nie jest możliwe. W takim przypadku można przekazać współrzędne klienta w formacie `lat,lon` (np. `52.2297,21.0122`).

## Uruchomienie w przeglądarce

### Lokalnie / Codespaces

```bash
pip install -e .
pip install streamlit
streamlit run app.py
```

### Hugging Face Spaces (Streamlit)

Wymagane pliki w Space: `app.py` oraz `pyproject.toml` (zawiera zależności, w tym `streamlit`). W konfiguracji Space ustaw „App file” na `app.py`.

## Testy

```bash
pip install -e .
python -m unittest discover -s tests
```
