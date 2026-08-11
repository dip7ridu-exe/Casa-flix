# ResenhaFlix V27 — Smart Manga + Internal SoundCloud + dLivros Finder

## Mangás
A busca agora considera:
- título inglês;
- romaji;
- título nativo;
- synonyms do AniList;
- tradução automática inglês → PT-BR via MyMemory;
- heurísticas de nomes comuns;
- aliases aprendidos de resultados anteriores.

Exemplo:
`The Infinite Mage` também tenta `Mago do Infinito` e `Mago Infinito`.

Quando um resultado traduzido é encontrado, o nome é salvo localmente para buscas futuras.

Para LycanToons existe ainda um atalho inteligente usando:
`https://lycantoons.com/series/<slug-do-alias>`

Ele é mostrado como `Atalho provável` quando não foi possível confirmar via CORS.

## Música / SoundCloud
- faixas SoundCloud são reproduzidas dentro do ResenhaFlix com o Widget oficial;
- cards SoundCloud mostram apenas `Ouvir inteira`;
- o player inferior não mostra botão para sair do ResenhaFlix quando a origem é SoundCloud;
- colar uma URL pública SoundCloud continua tocando dentro do site;
- pesquisa por nome no SoundCloud dentro do ResenhaFlix usa o Worker opcional incluído no ZIP;
- sem Worker, Audius/iTunes continuam como fallback, sem botão de pesquisa externa SoundCloud.

## Livros
Cada livro agora possui:
`🔎 Achar no dLivros`

O botão tenta montar a URL provável do livro usando título + autor.
O ResenhaFlix não importa nem automatiza downloads vindos do dLivros.

## PWA
Cache: `resenhaflix-shell-v27`
