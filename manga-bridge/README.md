# Manga Bridge V15

Backend opcional para fontes que bloqueiam CORS.

## Local
```bash
pip install -r requirements.txt
uvicorn server:app --port 8787
```

Depois configure no ResenhaFlix:
`Configurações → Manga Bridge → http://localhost:8787`

## Endpoints
- GET /api/health
- POST /api/search
- POST /api/batch/search
- POST /api/popular
- POST /api/manga
- POST /api/chapter
- GET /api/image

O parser é genérico. Fontes com API própria, WebView, captcha, login, paywall ou lógica Kotlin específica podem precisar de um adaptador próprio.
