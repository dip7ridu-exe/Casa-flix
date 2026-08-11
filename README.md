# ResenhaFlix V25 — Manga Direct + Full Music + Better Books

## Mangás
- Busca em até 15 fontes PT/PT-BR do Keiyoushi.
- As fontes confirmadas ficam no topo.
- O ranking considera:
  - correspondência do título;
  - URL exata encontrada;
  - idioma PT/PT-BR;
  - histórico de fontes já abertas com sucesso.
- Quando a busca consegue uma URL exata, `Ler agora` abre diretamente a página daquele mangá.
- Se CORS/anti-bot impedir confirmar a página, a fonte fica separada como `Abrir busca`.
- O ResenhaFlix não afirma que o mangá existe em uma fonte sem confirmação.

## Música
O player inferior foi redesenhado com visual inspirado em aplicativos de streaming:
- capa + faixa + artista à esquerda;
- aleatório / anterior / play / próxima / repetir no centro;
- timeline;
- origem / fila / volume à direita;
- versão mobile compacta.

### Faixas completas
A V25 adiciona Audius:
- Base padrão `https://api.audius.co`;
- campo para API Key do Audius;
- faixas Audius recebem selo `COMPLETA`;
- o player usa o endpoint de stream da própria plataforma;
- iTunes continua como catálogo/previews;
- JSON personalizado continua funcionando.

Não existe download de música.

## Livros
A preferência de formato agora é:

1. PDF
2. EPUB
3. MOBI
4. HTML
5. TXT

Para itens marcados como domínio público/liberados:
- PDF abre no leitor do navegador;
- EPUB abre com epub.js;
- MOBI fica disponível para download;
- formatos disponíveis aparecem individualmente no card;
- `Melhor download` segue PDF > EPUB > MOBI.

## Observação sobre a referência de livros
A URL do site de livros mencionada pelo usuário não veio na mensagem desta atualização.
Por isso a V25 mantém Open Library + Gutendex/Project Gutenberg e melhora o fluxo de leitura/download.
Quando a URL de referência for fornecida, o layout pode ser aproximado dela.

## PWA
Cache: `resenhaflix-shell-v25`
