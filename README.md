# CasaFlix V10 — Mobile Tested

## Pular abertura
- Em séries/animes, aparece `Pular abertura ⏭` durante os primeiros 150 segundos.
- Ao tocar, avança 90 segundos a partir da posição atual.
- O botão some depois de ser usado naquele episódio.

## Próximo episódio
Ao tocar em Próximo episódio, a V10 leva para o episódio seguinte:
1. o addon/fonte atual,
2. o nome da fonte quando ainda existir,
3. a qualidade usada,
4. fallback para a melhor fonte disponível.

O episódio seguinte começa automaticamente. A posição do episódio anterior é salva antes da troca.

## Mobile / Minha Lista
A rolagem vertical foi refeita para depender do documento normal, não de containers internos.
- `html`, `body`, `#page` e `#pageBody` não ficam presos em altura fixa.
- Minha Lista usa 2 colunas em celulares e pode crescer indefinidamente para baixo.
- detalhes/configurações não deixam `overflow:hidden` preso no body.
- backdrop-filter foi removido da navegação mobile para reduzir glitches de composição/touch.
- o scroll horizontal dos carrosséis continua funcionando sem bloquear o gesto vertical.

## Testes
A versão foi preparada para teste em viewport mobile com dezenas de itens na Minha Lista.

## PWA
Cache: `casaflix-shell-v10`. Envie todos os arquivos ao GitHub Pages.
