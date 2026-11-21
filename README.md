# Curiosidade Infinita — Editor de Shorts

Editor gratuito via GitHub Actions: gera narração em português brasileiro usando edge-tts e substitui o áudio de um MP4 usando FFmpeg.

## Como usar no celular
1. Na aba **Code**, abra a pasta `videos` e envie o vídeo MP4 usando **Add file > Upload files** (se a pasta estiver vazia, crie primeiro um arquivo nela). GitHub pelo navegador pode exigir **Site para computador**. Upload web limitado a 25 MB por arquivo.
2. Abra **Actions > Gerar Short com voz brasileira > Run workflow**.
3. Informe o caminho exato do vídeo, por exemplo `videos/short.mp4`.
4. Edite o campo do roteiro se desejar e clique em **Run workflow**.
5. Quando finalizar, abra a execução e baixe o arquivo em **Artifacts**: `short-final` (ZIP contendo MP4).

**Importante:** o áudio original é substituído integralmente, inclusive eventual música. Não publica automaticamente no YouTube. O tempo do vídeo é mantido; a narração é acelerada ou desacelerada moderadamente para caber. O GitHub Actions precisa de internet e pode sofrer alterações de disponibilidade do serviço gratuito de voz.

**Privacidade:** este repositório está público. Mude para privado em **Settings > General > Danger Zone > Change repository visibility** antes de enviar vídeos privados.

## Voz
Padrão: `pt-BR-ThalitaMultilingualNeural`. Alternativa: `pt-BR-FranciscaNeural`. O roteiro padrão é uma adaptação do Short sobre o corredor de buracos negros; confira a correspondência com as legendas existentes.
