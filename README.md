## Instalacja i uruchomienie

## Wymagania wstępne:

Na komputerze zainstalowane muszą być:

- ollama
- python >= 3.12
- uv

## Uruchomienie skrytpu:

1. `$ git clone xxx`
2. `$ cd xx`
3. `uv install`
4. `python search_papers.py`
5. `python summarize_with_llm.py`

Plik .json z pobranymi abstraktami prac z arxiv zapisany jest w katalogu `~/papers`.
Wygenerowane podsumowanie dostępne jest w pliku `~/papers/summary.md`
Czas generowania podsumowań zależny jest od ilości prac, LLM-a i zasobów sprzętowych (RAM, CPU, GPU).
Polecam uruchamiać LLM korzystając z GPU.
