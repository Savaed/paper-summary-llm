> **Wyszukiwanie i streszczanie abstraktów publikacji dostępnych na [arxiv](https://arxiv.org/)
> za pomocą lokalnie zainstalowanego modelu językowego (LLM).**

## Wymagania wstępne

Na komputerze zainstalowane muszą być:

- [ollama](https://ollama.com/),
- [python](https://www.python.org/) >= 3.12,
- [uv](https://docs.astral.sh/uv/).

## Uruchomienie skrytpu

1. Pobranie kodu z repozytorium GitHub:

```terminal
$ git clone https://github.com/Savaed/paper-summary-llm.git
```

2. Przejście do katalogu roboczego:

```terminal
$ cd paper-summary-llm
```

4. Zainstalowanie potrzebnych pakietów python w wirtualnym środowisku:

```terminal
$ uv sync
```

4. Aktywacja wirtualnego środowiska:

```terminal
$ . .venv/bin/activate
```

4. Wyszukanie abstraktów prac:

```terminal
$ python search_papers.py
```

5. Podsumowanie za pomocą lokalnego LLM-a:

```terminal
$ python summarize_with_llm.py
```

## Uwagi

- Konfiguracja dostępna w pliku `config.json`.
- Promptem i formatem odpowiedzi LLM-a można (do pewnego stopnia) sterować korzystając z pliku
  `template.tmpl`.
- Plik `.json` z pobranymi abstraktami prac z arxiv zapisywany jest w katalogu `~/papers`.
- Wygenerowane podsumowanie dostępne jest w pliku `~/papers/summary.md`.
- Czas generowania podsumowań zależny jest od ilości prac, LLM-a i zasobów sprzętowych (RAM, CPU,
  GPU).
- Każde kolejne podsumowanie jest **dodawane** do pliku `~/summary.md`.
- Testowane na Linuxie.
- Polecam uruchamiać LLM korzystając z GPU.
