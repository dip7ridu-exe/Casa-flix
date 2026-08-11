# ResenhaFlix V29 — Global More + Correct Metadata + Trailers

## Pesquisa global
Agora cada grupo é separado:
- Filmes
- Séries
- Animes
- Músicas
- Artistas
- Mangás
- Livros

Cada seção possui `Ver mais ›`.
O botão abre uma página completa daquela categoria mantendo a mesma pesquisa.

Os resultados são guardados por alguns minutos, então abrir `Ver mais` normalmente não repete todas as consultas.

## Correção: clicar em um filme e abrir outro
A identidade do card não usa mais apenas `type + id`.

Agora:
- IDs IMDb (`tt...`) podem ser compartilhados entre addons;
- IDs customizados são vinculados ao manifesto que os criou;
- cada card guarda uma chave exclusiva para o objeto exato;
- metadata customizada é pedida primeiro ao addon que criou o item;
- Cinemeta só é usado automaticamente para IDs IMDb;
- se um addon customizado não retornar detalhes válidos, o ResenhaFlix mantém os dados do card em vez de consultar outro filme.

Também foi corrigido um caso em que um item sem `type` podia assumir `movie` mesmo vindo de catálogo de séries.

## Trailer no detalhe
A área de imagem dos detalhes agora suporta trailer:
- procura `meta.trailers`;
- também aceita `meta.trailerStreams`;
- YouTube ID é incorporado no hero;
- autoplay silencioso;
- botão 🔇 / 🔊;
- se não existir trailer, a imagem de fundo continua normalmente;
- o trailer é carregado depois da metadata principal para não atrasar a abertura.

## Desempenho
- busca de catálogos tem timeout curto;
- menos catálogos redundantes são consultados por manifesto;
- resultados da pesquisa têm cache;
- metadata detalhada tem cache;
- animações usam principalmente transform/opacity;
- trailer e recomendações são carregados depois do conteúdo principal.

## Mobile
- `Ver mais` usa duas colunas para filmes/animes/mangás;
- livros permanecem em uma coluna;
- detalhe continua fullscreen;
- trailer fica atrás dos gradientes e dos controles;
- animações respeitam `prefers-reduced-motion`.

## PWA
Cache: `resenhaflix-shell-v29`.
