# ResenhaFlix Manga Bridge V30

O Bridge é recomendado para conseguir ler dentro do ResenhaFlix quando as fontes bloqueiam CORS.

Adaptadores incluídos:
- Madara / WordPress (inclui busca AJAX, capítulos AJAX e leitor de páginas);
- Saikai Scan (API usada pela extensão atual);
- LycanToons (API JSON `/api/series`);
- Mangás Brasuka (busca JSON e capítulos serializados pelo Next.js);
- parser HTML genérico.

Fontes que exigem login, captcha, WebView ou lógica Kotlin específica podem continuar incompatíveis até receberem um adaptador próprio.

## Rodar local

```bash
pip install -r requirements.txt
uvicorn server:app --port 8787
```

Depois coloque `http://localhost:8787` em:
ResenhaFlix → Configurações → Mangás → Manga Bridge.

## Render

O `render.yaml` já está preparado. Após publicar, use a URL HTTPS do serviço no campo Manga Bridge.
