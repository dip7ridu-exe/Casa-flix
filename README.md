# ResenhaFlix V28 — Manga Fast + Books PT-BR + Netflix Details

## Mangás
Correções principais:
- selecionar `5 fontes` agora pesquisa exatamente 5;
- não existe mais busca escondida em 15 fontes;
- aliases PT-BR são calculados uma vez por busca;
- cada fonte tenta no máximo 3 nomes prioritários;
- endpoints de busca da fonte são tentados em paralelo;
- timeout foi reduzido;
- links `/series/<slug>` inventados foram removidos.

URLs diretas só aparecem quando:
1. a própria busca da fonte devolveu a URL; ou
2. existe um mapeamento explicitamente validado.

Exemplo validado:
`The Infinite Mage` → `Mago do Infinito`
LycanToons:
`https://lycantoons.com/series/mago-do-infinito`

## Livros
- Open Library exige `language:por`;
- `lang=pt` é enviado para priorizar edição em português;
- quando existe edição portuguesa no resultado, o título dessa edição é usado;
- Gutendex agora usa somente `languages=pt`;
- dLivros não recebe mais slugs inventados.

O botão `Procurar no dLivros` faz uma pesquisa restrita ao domínio `dlivros.com/livro`, evitando os erros 404 causados por URLs adivinhadas.

## Filmes / Séries / Animes
Tela de detalhes redesenhada inspirada no fluxo visual da Netflix:
- backdrop grande;
- gradientes cinematográficos;
- título em destaque;
- botão Assistir / Continuar;
- Minha Lista circular;
- Gostei;
- metadados e HD;
- sinopse em coluna;
- elenco / gêneros;
- episódios para séries;
- Títulos semelhantes;
- layout desktop e mobile separados.

## PWA
Cache: `resenhaflix-shell-v28`.
