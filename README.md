# ResenhaFlix V24 — Manga Sources + Música + Livros

## Mangás
A área de Mangás foi simplificada para somente:
- Explorar
- Biblioteca

Não existe mais leitura de mangá dentro do ResenhaFlix.

Ao tocar em `Buscar fontes`, o site lê o repositório Keiyoushi, seleciona somente fontes PT/PT-BR e consulta entre 5 e 15 fontes (10 por padrão). Resultados confirmados aparecem primeiro. Se CORS impedir a confirmação, o botão abre a busca no site original e não afirma que o título foi encontrado.

## Música
Nova página com:
- Faixas
- Álbuns
- Artistas
- iTunes Search API como padrão
- prévia de áudio quando fornecida pela API
- URLs JSON adicionais
- importação de `.json`

O ResenhaFlix não cria download de música.

## Livros
Nova página com:
- Todos
- Grátis
- Minha estante

Fontes:
- Open Library para busca geral
- Gutendex / Project Gutenberg para obras gratuitas

Downloads e leitor interno só aparecem em itens marcados como domínio público/liberados.

Formatos:
- EPUB
- HTML
- TXT
- PDF

EPUB usa epub.js carregado somente quando necessário.

## APIs / URLs / JSON
Nas páginas Música ou Livros, toque em `⚙ Fontes`.

Você pode:
- trocar a API principal;
- adicionar URLs JSON;
- usar `{query}` na URL;
- importar arquivo `.json`.

Exemplos:
- `examples/music-source.example.json`
- `examples/books-source.example.json`

## PWA
Cache: `resenhaflix-shell-v24`
