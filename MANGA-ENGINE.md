# ResenhaFLIX Manga Engine

Modulo de mangas inspirado na separacao de responsabilidades do HakuNeko:

1. **Connector** consulta uma fonte e normaliza os dados.
2. **Manga** contem metadados e a biblioteca local.
3. **Chapter** lista idioma, grupo, data e paginas.
4. **Reader** exibe as paginas e salva o progresso.
5. **Download job** baixa as imagens com limite de concorrencia e monta um arquivo CBZ no navegador.

## Recursos

- Busca por titulo e nomes alternativos, com ranking de correspondencia.
- PT-BR como idioma padrao e troca rapida de idioma.
- Catalogo e capitulos pelo endpoint publico do MangaDex.
- Leitor vertical ou pagina a pagina.
- Qualidade economica ou original, ajuste de largura, espacamento e brilho.
- Progresso salvo localmente por capitulo.
- Biblioteca local.
- Fila e historico de downloads.
- Download CBZ sem biblioteca externa e sem enviar as imagens ao ResenhaFLIX.
- Interface responsiva para celular e desktop.

## Arquivos

- `manga-hakuneko.js`: motor, conector, leitor e gerenciador de downloads.
- `manga-hakuneko.css`: interface isolada pelo prefixo `hk-`.
- `index.html`: carrega o modulo depois do codigo principal e substitui somente a pagina de mangas.
- `service-worker.js`: inclui os arquivos do modulo no shell offline.

## Observacoes

O download e montado em memoria no aparelho. Capitulos muito grandes podem usar bastante RAM, principalmente em qualidade original. A disponibilidade de titulos, idiomas e capitulos depende da fonte. O usuario deve baixar somente material que tenha permissao para armazenar.
