# ResenhaFlix V22 — Smooth Player

## Player
- Topo agora mostra somente `Trocar fonte` e `Fechar`.
- Áudio, legenda, proporção e fullscreen ficam na barra inferior.
- Proporção foi removida completamente da área de Fontes.
- Botões centrais de voltar/avançar 10s usam SVG próprio para evitar os ícones quebrados.
- O painel de Fontes continua lateral no PC e bottom sheet no celular.

## Desempenho
- HLS.js não é mais baixado ao abrir o site; só é carregado quando uma fonte `.m3u8` precisa dele.
- Imagens de cards usam `loading=lazy`, `decoding=async` e prioridade baixa.
- Seções fora da tela usam `content-visibility`.
- Catálogos extras da Home são carregados depois do conteúdo principal.
- A rotação de cards não bloqueia mais a primeira renderização tentando páginas com `skip`.
- Eventos de mousemove/scroll/resize foram limitados com requestAnimationFrame/debounce.
- Efeitos caros de backdrop blur foram reduzidos.
- Durante scroll, animações de hover são suspensas.

## Catálogo
A rotação principal passou para janelas de aproximadamente 3 horas.
Uma página alternativa do catálogo é aquecida em background e usada nas próximas navegações quando estiver disponível.

## PWA
Cache: `resenhaflix-shell-v22`
