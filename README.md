# WhatsApp AI Backend — hsbteleet.com

Backend-only WhatsApp assistant for HSBTE LEET / Haryana LEET. There is **no frontend**. WhatsApp Cloud API talks to this FastAPI server; the server loads conversation memory from Supabase, knowledge from Excel, calls Gemini, and replies on WhatsApp.

## 1. What it does

A student messages the business WhatsApp number. Meta posts a webhook. The backend verifies the request, loads that user's memory, searches Excel knowledge, asks Gemini for a WhatsApp-friendly reply, stores the turn in Supabase, and sends the text through the Cloud API.

## 2. Architecture

```
USER → Meta WhatsApp Cloud API → FastAPI webhook
  → signature + parse + idempotency
  → Supabase (users, messages, memory, preferences)
  → Excel knowledge search (not a database)
  → Gemini (text only)
  → response validation
  → Meta send message → USER
```

Excel is the editable knowledge source. Supabase is the application database. Do not invert that.

## 3. Folder structure

```
whatsapp-ai-backend/
  app/                 FastAPI app, services, models
  data/                Excel knowledge files
  scripts/import_excel.py
  supabase/schema.sql
  tests/
  Dockerfile
  .env.example
```

## 4. Installation

```powershell
cd whatsapp-ai-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\import_excel.py
copy .env.example .env
```

Fill `.env` with real secrets. Never commit `.env`.

## 5. Environment variables

See `.env.example`. Required in production:

- `META_APP_SECRET` — HMAC for `X-Hub-Signature-256` (not the WhatsApp access token)
- `META_VERIFY_TOKEN` — token you configure in Meta for GET verification
- `WHATSAPP_ACCESS_TOKEN` — Graph API bearer token
- `WHATSAPP_PHONE_NUMBER_ID` — sender (AI cannot change this)
- `GEMINI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` — server-side only

`META_APP_SECRET` and `WHATSAPP_ACCESS_TOKEN` are different values. Both stay in `.env`.

## 6. Supabase setup

1. Create a project.
2. SQL editor → paste `supabase/schema.sql`.
3. Put project URL and **service role** key in `.env`.
4. Do not use the anon key for this backend.

## 7. Database SQL

Tables: `users`, `messages`, `conversation_memory`, `conversation_summaries`, `users_preferences`, `webhook_events`, `ai_logs`. Indexes are in the same file. Optional `knowledge_embeddings` + pgvector is commented for a later RAG phase.

## 8. Excel format

Same columns in every workbook: `category, subcategory, title, question, answer, keywords, url, branch, exam, priority, active`. Details in `data/README.md`. Sample data is generated from `whatsapp-bot-kit` CSVs via `python scripts/import_excel.py`.

## 9. Meta WhatsApp setup

1. Meta Developer App → WhatsApp product.
2. Add the webhook URL: `https://<your-domain>/webhook/whatsapp`
3. Verify token = `META_VERIFY_TOKEN`.
4. Subscribe to `messages`.
5. Copy App Secret, access token, and phone number ID into `.env`.

## 10. Webhook setup

Meta requires **public HTTPS**. Locally use Cloudflare Tunnel or ngrok (do not store tunnel tokens in git):

```text
https://<tunnel-host>/webhook/whatsapp
```

## 11. Verify token

GET `/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=<token>&hub.challenge=<n>`

Returns the challenge only when the token matches `META_VERIFY_TOKEN` (constant-time compare).

## 12. App Secret usage

POST webhooks must include `X-Hub-Signature-256`. The server HMACs the **raw body** with `META_APP_SECRET`. Invalid signatures are rejected. Signatures and secrets are never logged.

## 13. Gemini setup

Create a Google AI Studio key. Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` (default `gemini-2.0-flash`). Model name lives in config, not scattered through services.

## 14. Local development

```powershell
uvicorn app.main:app --reload --port 8000
```

Health: `http://localhost:8000/health`

## 15. Public HTTPS webhook

Point Meta at the tunnel URL. Keep `REQUIRE_WEBHOOK_SIGNATURE=true`.

## 16. Production deployment

Works on Render, Railway, Fly.io, VPS, AWS, GCP. Set env vars on the host. Do not copy `.env` into the image.

```powershell
docker build -t whatsapp-ai-backend .
docker run --env-file .env -p 8000:8000 whatsapp-ai-backend
```

OpenAPI `/docs` is disabled when `ENVIRONMENT=production`.

## 17. Security

- No browser UI, no CORS `*`, no client secrets
- HMAC webhook verification, admin key for reload
- Rate limit per WhatsApp user
- Prompt-injection: Excel and user text are data, not instructions
- Gemini cannot send WhatsApp, run tools, or pick the sender ID
- Recipient comes from the verified webhook `from` field
- Logs redact secrets and mask phone numbers
- Secrets are never returned in API or WhatsApp replies

## 18. Troubleshooting

| Symptom | Check |
| --- | --- |
| GET verify 403 | `META_VERIFY_TOKEN` mismatch |
| POST 403 | App Secret / signature over raw body |
| Duplicate replies | `messages.whatsapp_message_id` unique |
| Empty knowledge | run `import_excel.py`, then reload |
| Gemini fallback text | key, quota, model name |
| WhatsApp send failed | token, phone number ID, recipient format |

## 19. Testing

```powershell
pytest
```

## 20. How to add Excel knowledge

1. Open `data/faq.xlsx` or `data/knowledge.xlsx`.
2. Add a row (`active=true`, real URL only).
3. `POST /admin/reload-knowledge` with header `X-Admin-Key: <ADMIN_API_KEY>`.

No code change is required for new rows.
