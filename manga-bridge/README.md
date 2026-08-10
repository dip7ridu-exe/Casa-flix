# ResenhaFlix Manga Bridge

O GitHub Pages é estático e não consegue fazer requisições para muitos sites de mangá por causa de CORS, cookies e proteção de hotlink.

Este bridge:
- valida a fonte contra o repositório Keiyoushi;
- pesquisa mangás em fontes web compatíveis;
- lê detalhes e capítulos;
- extrai páginas;
- faz proxy das imagens com URL assinada;
- nunca executa o APK/JAR Android da extensão;
- não tenta quebrar DRM, login, paywall ou desafio anti-bot.

## Rodar local

```bash
pip install -r requirements.txt
uvicorn server:app --reload --port 8787
```

No ResenhaFlix:
`Configurações → Manga Bridge → http://localhost:8787`

## Render

Há um `render.yaml`. Crie um Web Service usando esta pasta/repositório e depois coloque a URL pública no ResenhaFlix.

## Compatibilidade

O parser genérico cobre layouts web comuns, especialmente sites com estruturas equivalentes a Madara/WordPress e leitores HTML tradicionais.
Fontes Keiyoushi que usam APIs próprias, GraphQL específico, WebView, tokens ou lógica Kotlin personalizada precisam de um adaptador específico no bridge para funcionar 100%.
