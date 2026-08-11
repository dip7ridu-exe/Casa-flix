# ResenhaFlix V23 — Stable Playback

## Botão Fontes
- O botão `Trocar fonte` ganhou espaço próprio.
- Foi movido visualmente para a esquerda.
- Existe uma pequena divisória antes do botão X.
- No mobile o espaçamento é menor, mas os dois botões não se sobrepõem.

## Reprodução mais estável
A V23 diferencia:
1. fonte que não inicia;
2. fonte que inicia, mas fica travando durante o filme/episódio.

### Monitor de buffering
Durante a reprodução o ResenhaFlix observa:
- `waiting`;
- `stalled`;
- tempo contínuo sem buffer suficiente;
- travamentos repetidos em uma janela de 90 segundos.

Quando uma fonte fica instável:
- salva a posição atual;
- penaliza essa fonte no ranking;
- tenta outra fonte automaticamente;
- continua aproximadamente do mesmo segundo;
- se nenhuma alternativa funcionar, tenta voltar para a fonte anterior.

### Aprendizado
O histórico de fontes agora também salva:
- quantidade de travamentos;
- travamentos graves;
- último travamento;
- duração do último travamento.

Isso reduz a chance de um episódio futuro escolher novamente uma fonte que iniciou normalmente, mas travou muito.

## HLS
- `loadVideo()` agora é aguardado antes do teste da fonte.
- Buffer máximo aumentado.
- HLS adaptativo usa margem mais conservadora ao subir qualidade.
- Uma falha de rede recebe uma tentativa de `startLoad()`.
- Uma falha de mídia recebe uma tentativa de `recoverMediaError()`.
- Depois disso entra a troca automática de fonte.

## Arquivos diretos
O elemento `<video>` passa para `preload=auto` durante a reprodução para permitir que o navegador faça buffer à frente.

## PWA
Cache: `resenhaflix-shell-v23`.
