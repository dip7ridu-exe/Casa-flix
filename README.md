# CasaFlix V11 — Smart Sources

## Fontes que falham em alguns episódios
A V11 não assume mais que a maior resolução é a melhor fonte.

Quando abre um episódio:
1. prioriza a fonte/provedor que funcionou anteriormente;
2. testa a fonte;
3. espera o vídeo realmente chegar em `canplay/playing`;
4. se der erro fatal ou ficar 14s sem iniciar, marca a fonte como falha;
5. tenta automaticamente a próxima;
6. quando encontra uma que funciona, salva o provedor para os próximos episódios.

O histórico de sucesso/falha influencia a ordem das fontes futuras.

### Exemplo usado no teste
The Big Bang Theory — temporada 3, episódio 21:
- 1080p simulada como indisponível;
- outra 1080p simulada como indisponível;
- RedeFlix 720p simulada como funcional.

Resultado esperado: CasaFlix abandona as fontes quebradas e inicia RedeFlix 720p automaticamente.
No episódio seguinte, RedeFlix recebe prioridade.

## Pular abertura adaptativo
Sem um horário aprendido:
- o botão pode aparecer do começo até 60% do episódio, limitado a 30 minutos;
- isso cobre séries que têm cold open ou abertura perto do meio.

Na primeira vez que você usa `Pular abertura`, o CasaFlix aprende:
- série;
- temporada;
- horário aproximado em que a abertura começou;
- duração da abertura.

Nos episódios seguintes, o botão aparece perto daquele horário aprendido.

`Ajustar abertura` permite:
- marcar a posição atual como início;
- escolher 60/90/120s;
- esquecer o perfil aprendido.

## Troca automática
Pode ser ligada/desligada no player por `⚡ Troca automática`.

## Mobile
Mantém as correções de scroll/touch da V10.

## PWA
Cache: `casaflix-shell-v11`.
