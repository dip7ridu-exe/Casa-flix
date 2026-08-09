# CasaFlix V9 — Mobile Stable

## O que mudou no celular
- A busca não abre mais uma camada fixa sobre o site.
- O botão 🔎 abre diretamente a página de pesquisa.
- Scroll horizontal dos cards foi simplificado.
- Menos overlays e menos elementos invisíveis capturando toque.
- Estado de modais/touch é reparado ao voltar para a página, girar o aparelho ou redimensionar.
- Menus fechados usam `pointer-events: none`.

## Outro player
O botão `Outro player` aparece no player e em cada fonte direta.

Ele oferece:
1. Compartilhar a URL com outro app do celular.
2. Abrir a fonte em nova aba.
3. Copiar a URL da fonte para colar em VLC/outro player.

## Proporção
O player usa moldura 16:9 e agora tem menu de proporção:
- Auto 16:9 (padrão)
- 16:9 sem distorcer
- Forçar 16:9
- Preencher 16:9
- Original

No modo Auto, fontes claramente verticais/3:4 são corrigidas automaticamente.
Se uma fonte continuar errada, selecione `Forçar 16:9`.

## PWA
Cache atualizado para `casaflix-shell-v9`.

Envie todos os arquivos ao GitHub Pages:
- index.html
- manifest.webmanifest
- service-worker.js
- icons/
