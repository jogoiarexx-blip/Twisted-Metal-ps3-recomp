# Resultado dos logs de 2 de outubro de 2026

## Identidade do executável

- Duas inicializações no log principal chegaram ao jogo BCUS98106.
- Disco: `APP_VER=01.00`, caminho `E:/01 jogos/Emulador ps3/01 roms/twisted/PS3_GAME/USRDIR/EBOOT.BIN`.
- Atualização encontrada: `APP_VER=01.06`, executável efetivo `/dev_hdd0/game/BCUS98106/USRDIR/EBOOT.BIN`.
- Hash PPU efetivo registrado pelo RPCS3: `PPU-6bb4db395550102f567fb7b1dbbf81583417150f`.
- A contagem de descritores em `elf-map.json` pertence ao ELF 1.00 do disco, portanto não é a base adequada para a sessão 1.06.

## Configuração efetiva registrada

- CPU: Intel Core i5-11400, 12 threads; GPU selecionada: NVIDIA GeForce RTX 4060, Vulkan.
- PPU Decoder: LLVM; SPU Decoder: ASMJIT; SPU Block Size: Mega.
- Resolution Scale: 150%; buffers de cor e profundidade de leitura e escrita ativos.
- Patches aplicados: `Unlock FPS` e `Skip Intro`. O log não registra aplicação de `Disable SPU MLAA`.
- Configuração personalizada carregada de `config/custom_configs/config_BCUS98106.yml`.
- Há mensagem `invalid enum` para `Async Shader Recompiler` na configuração global, embora a configuração efetiva liste `Async Recompiler with Shader Interpreter`.

## Falha separada do desempenho

Nas duas sessões ocorreu erro fatal dentro do RPCS3: `vm::writer_lock is being used without cpu_flag::wait set by the caller!`, durante `cellSpursRemoveWorkload`. Trata-se de falha reportada pelo emulador, não de evidência de que os arquivos `.psarc` estejam ausentes.

## Próxima entrada necessária

Um novo `EBOOT(1).elf` foi recebido e mapeado. Confirme se ele foi extraído de `E:/01 jogos/Emulador ps3/dev_hdd0/game/BCUS98106/USRDIR/EBOOT.BIN`; o mapa enviado `elf-map-local.json` ainda corresponde ao ELF antigo. Consulte `COMPARACAO-VERSOES.md`.
