# ResenhaFlix V20 — Manga Fallback + Source Priority

## Fontes de vídeo
A ordem configurada em Configurações → Avançado → Fontes de vídeo passou a definir prioridade.
A primeira linha vale mais, depois a segunda e assim por diante.

O sistema ainda considera:
- fonte principal escolhida no player;
- fonte que funcionou no episódio anterior;
- histórico de sucesso/falha;
- qualidade.

Os padrões distribuídos continuam FrostStream + WatchHub. Fontes adicionais já salvas pelo usuário são preservadas.

## Mangás
A V20 mantém o leitor nativo, mas adiciona um caminho que não depende dele funcionar.

### Modo site dentro do ResenhaFlix
Na página Explorar sempre aparece `Abrir uma fonte diretamente`.

As extensões instaladas aparecem Português primeiro.
Ao tocar em uma fonte, o site da fonte abre dentro de uma janela do próprio ResenhaFlix.

Se houver uma pesquisa, o ResenhaFlix tenta URLs comuns de busca.
O botão `Outra busca` alterna entre formatos de busca.

### Fallback automático
Se detalhes/capítulos não carregarem:
`Abrir este mangá no modo site`.

Se as páginas do capítulo não carregarem:
`Ler no modo site`.

### Extensões
Cada extensão tem novamente:
- Instalar / Instalada
- Abrir fonte

`Abrir fonte` usa o modo site interno.

## Limite do modo site
Alguns sites bloqueiam iframe via CSP/X-Frame-Options. A V20 não contorna essa proteção.
Nesses casos há `Abrir fora`.

## PWA
Cache: resenhaflix-shell-v20
