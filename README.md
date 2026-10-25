# Хмарні обчислення — лабораторні роботи

Автор: **Юлія Частухіна** · Хмара: **Google Cloud Platform**

## [Lab 1 — PARCS: паралельний brute-force підбір пароля](lab1-parcs-bruteforce/) (варіант 7.6)

Повний перебір простору ключів розподіляється між воркерами PARCS (master + N workers).
Кластер піднімається через Docker Compose, числа масштабування — реальним бенчмарком.

- Код джоби: [`solver.py`](lab1-parcs-bruteforce/solver.py)
- Кластер: [`docker-compose.yml`](lab1-parcs-bruteforce/docker-compose.yml) (1 master + 4 workers)
- Бенчмарк + графік: [`benchmark/`](lab1-parcs-bruteforce/benchmark/)
- **Звіт:** [`REPORT.md`](lab1-parcs-bruteforce/REPORT.md)

Швидкий старт:
```bash
cd lab1-parcs-bruteforce
N=4 docker compose up --build --scale worker=4 --abort-on-container-exit
cat output.txt            # PASSWORD FOUND: help
cd benchmark && ./run_benchmark.sh   # results.csv + results.png
```

## [Lab 2 — PoC: аудіо → Speech-to-Text → Gemini](lab2-speech-gemini/)

Сервіс, що приймає аудіо, розшифровує його через **Google Cloud Speech-to-Text**
і робить структурований конспект через **Gemini API**. FastAPI, деплой на Cloud Run.

- Код: [`app/`](lab2-speech-gemini/app/)
- **Презентація:** [`PRESENTATION.md`](lab2-speech-gemini/PRESENTATION.md)

---
Хмара за вибором — **Google Cloud** (не Azure).
