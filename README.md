# ResenhaFlix V15 — Manga Stable

## O que foi corrigido

### Explorar abre rápido
A tela Explorar não consulta todas as fontes ao abrir.
Ela carrega destaques pelo catálogo/cache e só pesquisa as fontes quando:
- você digita um título;
- toca em `Buscar nas fontes`;
- escolhe uma fonte rápida.

### Busca progressiva
Ao pesquisar um título:
1. fontes PT-BR/PT são consultadas primeiro;
2. as quatro primeiras são consultadas em paralelo;
3. resultados aparecem assim que cada fonte responde;
4. fontes secundárias continuam em background;
5. fontes que falham recentemente perdem prioridade por alguns minutos.

### Cards corrigidos
Todos os cards têm:
- título;
- capa;
- botão principal;
- botão `＋` / `✓` da Biblioteca.

Resultado vindo da fonte:
`▶ Ler capítulos`

Resultado apenas do catálogo:
`🔎 Buscar nas fontes`

### Biblioteca
A biblioteca aceita:
- títulos do catálogo;
- resultados reais de fontes.

Um título salvo apenas pelo catálogo continua pesquisável nas fontes quando você tocar para ler.

### Repositórios
Padrões:
1. Keiyoushi:
   https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.min.json
2. Aniyomi secundário:
   https://raw.githubusercontent.com/aniyomiorg/aniyomi-extensions/repo/index.min.json

O ResenhaFlix detecta extensões `animeextension` e não mistura essas extensões na tela de mangás.
O Keiyoushi `index.min.json` ainda possui fallback automático para `index.json`.

### Manga Bridge
Continua incluído em `manga-bridge/`.

A V15 também adiciona:
`POST /api/batch/search`

para permitir busca paralela de até 8 fontes no backend.

## Observação importante
As extensões Android do Mihon/Keiyoushi contêm lógica Kotlin própria.
O ResenhaFlix não executa os APK/JAR no GitHub Pages.

O modo direto funciona apenas em sites que permitem CORS e layouts compatíveis.
Para uma experiência consistente de:
busca → detalhes → capítulos → páginas → leitor vertical,
configure o Manga Bridge.

## PWA
Cache: resenhaflix-shell-v15
