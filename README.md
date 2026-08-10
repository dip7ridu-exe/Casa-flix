# ResenhaFlix V14 — Native Manga Reader

## Leitor nativo
A leitura não usa mais iframe/site original como fluxo principal.

Recursos:
- Vertical / Webtoon
- Página esquerda → direita
- Página direita → esquerda
- ajuste à largura / página inteira / tamanho original
- espaçamento 0 / 8 / 16 px
- controle de brilho
- trocar capítulo sem sair do leitor
- capítulo anterior / próximo
- progresso salvo por capítulo
- restauração da página/posição
- biblioteca de mangás
- busca diretamente nas fontes instaladas

## Fontes Keiyoushi
As extensões Keiyoushi continuam sendo a loja/lista de fontes.
O navegador não executa os APK/JAR Kotlin das extensões.

Para transformar fontes web compatíveis em:
busca → mangá → capítulos → páginas,
a V14 inclui `manga-bridge/`.

O frontend tenta acesso direto primeiro quando CORS permite. Quando não permite, usa o Manga Bridge configurado em:
Configurações → Manga Bridge.

## Manga Bridge
Pasta:
`manga-bridge/`

Inclui FastAPI, proxy seguro de imagens com assinatura e parser genérico para layouts web comuns.

## GitHub Pages
Continue hospedando o frontend no GitHub Pages.
O bridge precisa rodar em um serviço que execute Python, como Render/Railway/Fly/etc.

Depois, coloque a URL do bridge nas configurações do ResenhaFlix.

## PWA
Cache: resenhaflix-shell-v14
