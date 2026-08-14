# ResenhaFLIX Manga Engine v33

Modulo de mangas inspirado na separacao de responsabilidades do HakuNeko:

1. **Connector** consulta uma fonte e normaliza os dados.
2. **Manga** contem metadados e a biblioteca local.
3. **Chapter** lista idioma, grupo, data e paginas.
4. **Reader** exibe as paginas e salva o progresso.
5. **Download job** baixa as imagens com limite de concorrencia e monta um arquivo CBZ no navegador.

## Recursos

- Busca por titulo e nomes alternativos, com ranking de correspondencia.
- Seletor de conector inspirado no HakuNeko: todas as fontes, MangaDex ou fontes PT-BR.
- PT-BR como idioma padrao e troca rapida de idioma.
- Catálogo, capítulos e páginas do MangaDex pelo bridge, com fallback direto.
- Busca adicional em até quatro fontes PT-BR curadas a partir do Keiyoushi.
- Tela Fontes para configurar e testar o Manga Bridge no próprio site.
- Fallback automatico para o MangaDex direto quando um Bridge configurado fica offline.
- Link de configuracao para levar a mesma URL do Bridge do celular para o PC.
- Leitor vertical ou pagina a pagina.
- Qualidade economica ou original, ajuste de largura, espacamento e brilho.
- Progresso salvo localmente por capitulo.
- Acao rapida para marcar um capitulo como lido ou nao lido.
- Biblioteca local.
- Fila e historico de downloads.
- Download CBZ sem biblioteca externa; imagens passam pelo proxy assinado quando o bridge está ativo.
- Interface responsiva para celular e desktop.

## Arquivos

- `manga-hakuneko.js`: motor, conector, leitor e gerenciador de downloads.
- `manga-hakuneko.css`: interface isolada pelo prefixo `hk-`.
- `index.html`: carrega o modulo depois do codigo principal e substitui somente a pagina de mangas.
- `service-worker.js`: inclui os arquivos do modulo no shell offline.
- `manga-bridge/server.py`: proxy FastAPI para MangaDex e adaptadores PT-BR.
- `Dockerfile` e `railway.toml`: deploy do bridge sem alterar o GitHub Pages.

## PC e celular

A URL do Bridge e uma preferencia local do navegador. Na aba **Fontes**, use **Copiar link para outro aparelho** e abra o link no PC para importar a mesma configuracao. O backend v33 aceita o site publicado e, para desenvolvimento, origens `localhost` e `127.0.0.1` em qualquer porta. Nao abra o `index.html` diretamente por `file://`; use um servidor local.

## Observacoes

O download e montado em memoria no aparelho. Capitulos muito grandes podem usar bastante RAM, principalmente em qualidade original. O índice Keiyoushi descreve extensões Android em Kotlin; o navegador não executa os APKs e depende dos adaptadores reimplementados no bridge. A disponibilidade de títulos, idiomas e capítulos depende da fonte. O usuário deve baixar somente material que tenha permissão para armazenar.
