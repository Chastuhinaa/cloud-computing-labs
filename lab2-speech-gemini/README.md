# Lab 2 — PoC: Аудіо → Speech-to-Text → Gemini

FastAPI-сервіс: аудіо → розшифровка (Google Cloud Speech-to-Text) → структурований
конспект (Gemini). Деплой — Cloud Run. Презентація: [`PRESENTATION.md`](PRESENTATION.md).

## Локальний запуск (Docker)
```bash
docker build -t speech-gemini-poc .
docker run -p 8080:8080 \
    -e GEMINI_API_KEY=<твій_ключ_gemini> \
    -e GOOGLE_APPLICATION_CREDENTIALS=/creds/sa.json \
    -v /шлях/до/service-account.json:/creds/sa.json:ro \
    speech-gemini-poc
# перевірка:
curl http://localhost:8080/            # {"status":"ok",...}
curl -X POST http://localhost:8080/process -F "audio=@sample.wav"
```

## Деплой на Google Cloud Run
```bash
gcloud config set project <PROJECT_ID>
gcloud services enable run.googleapis.com speech.googleapis.com \
    artifactregistry.googleapis.com

# збірка та деплой одним кроком із джерел
gcloud run deploy speech-gemini-poc \
    --source . \
    --region europe-central2 \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY=<твій_ключ_gemini>,LANGUAGE_CODE=uk-UA

# сервісний акаунт Cloud Run має роль roles/speech.client — доступ до Speech-to-Text
# без ключів у коді (ADC).
```

## Ендпоінти
- `GET /` — health-check.
- `POST /process` — `multipart/form-data`, поле `audio`; повертає `{ transcript, summary }`.

> Ключі та `service-account.json` НЕ комітити (див. `.gitignore`).
