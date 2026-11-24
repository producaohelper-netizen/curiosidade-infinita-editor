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

## Novo modo: editar com Concat

O workflow **Editar Short com Concat** instala o Concat oficial v0.2.12 no runner Linux do GitHub, verifica o SHA-256 do instalador e usa sua API MCP headless (sem abrir janela). O editor Python anterior continua disponível, sem alterações.

1. Envie um MP4 para a pasta `videos/`.
2. Depois de incorporar a integração à branch principal, abra **Actions > Editar Short com Concat > Run workflow**.
3. Informe o caminho do vídeo. O campo título é opcional e aparece nos primeiros três segundos; o campo roteiro é opcional (vazio preserva o áudio original; preenchido substitui todo o áudio pela narração do editor anterior).
4. Baixe o artifact **concat-final** contendo `concat-final.mp4` (1080 × 1920, 30 fps, H.264).

O Concat roda no runner, não no seu celular. Este modo automatiza importação, timeline, título e exportação; ainda não oferece a interface gráfica, legendas automáticas ou edição interativa pelo navegador. Projetos temporários são removidos; o MP4 final é o artifact. Vídeos e logs do repositório público não devem conter material privado. O runner precisa de internet para instalação e narração opcional. A integração precisa passar no teste de renderização do workflow.

Para usar localmente, instale [Concat](https://github.com/jub0t/Concat/releases/tag/v0.2.12) e execute, na raiz deste repositório:

```sh
python concat_editor.py --video videos/SEU_VIDEO.mp4 --title "Curiosidade Infinita" --binary concat
```

No Windows, se o executável não estiver no PATH, use `--binary "C:\Program Files\Concat\concat.exe"` ou o caminho real da sua instalação. A saída deve ser um arquivo novo.

Concat é um software independente licenciado sob [AGPL-3.0-or-later](https://github.com/jub0t/Concat/blob/v0.2.12/LICENSE); esta integração usa o executável oficial sem modificá-lo. [Documentação MCP](https://github.com/jub0t/Concat/blob/v0.2.12/docs/MCP.md).
