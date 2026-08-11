# ResenhaFlix V26 — Global Search + SoundCloud + Books Fast + Manga Repo Fix

## Mangás
O problema principal das fontes foi corrigido:
- a V25 usava `index.min.json`;
- o índice atual completo do Keiyoushi está em um novo formato dentro de `index.json`;
- a V26 entende `extensionList.extensions`;
- filtra PT/PT-BR;
- mantém ranking e busca em até 15 fontes.

O navegador ainda pode ser impedido por CORS/anti-bot de confirmar a página exata em algumas fontes. Nesses casos a fonte continua aparecendo como alternativa, sem falso positivo.

## Música
### SoundCloud
- suporte ao player/widget oficial do SoundCloud;
- colar uma URL pública do SoundCloud na busca toca a faixa pelo widget oficial;
- botão de busca externa no SoundCloud;
- Worker opcional para pesquisar SoundCloud dentro do ResenhaFlix;
- Worker guarda Client Secret fora do GitHub Pages;
- resultados SoundCloud entram antes de Audius/iTunes quando o Worker está configurado.

Arquivos:
- `soundcloud-worker/worker.js`
- `soundcloud-worker/README.md`

Audius e iTunes continuam como fallback.

## Livros
- página organizada por categorias;
- leitura rápida prefere PDF;
- se PDF não existe, HTML vem antes de EPUB para abrir mais rápido;
- epub.js é pré-carregado em segundo plano ao entrar em Livros;
- Open Library agora pede `ebook_access`, `ia` e `public_scan_b`;
- livros com acesso público podem consultar o Metadata API do Internet Archive para descobrir PDF/EPUB/MOBI;
- formatos são atualizados em background sem segurar a primeira renderização.

Downloads continuam restritos a itens classificados como públicos/liberados pelas fontes usadas.

## Busca global
A barra principal agora pesquisa:
- Filmes
- Séries
- Animes
- Músicas
- Artistas
- Mangás
- Livros

Cada grupo carrega em paralelo, então uma API lenta não bloqueia as demais.

## PWA
Cache: `resenhaflix-shell-v26`
