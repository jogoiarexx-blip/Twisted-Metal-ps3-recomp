# Cruzamento v0.8 — Twisted Metal BCUS98106

## Entradas verificadas
- `EBOOT.elf`: SHA-256 `41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d`
- `rpcs3-0.0.43.zip`: código-fonte do emulador, não um jogo ou build de execução.
- Base de recompilação v0.7: três funções curtas, início da execução e implementação parcial de TLS.

## O que mudou
- Novo `CROSSCHECK.py` valida o hash, ELF big-endian PowerPC, entrada, os bytes originais das três funções já geradas e a integridade dos metadados de importações.
- Cruzamento opcional com a árvore de código-fonte RPCS3 para confirmar a presença do código SPU e do renderizador Vulkan.
- Este script não modifica o jogo ou o RPCS3. Não promete ganho de FPS.

## Testes feitos neste ambiente
- `python CROSSCHECK.py /mnt/data/EBOOT.elf --rpcs3-source /mnt/data/rpcs3-0.0.43.zip`: 13/13 verificações passaram.
- `g++ -std=c++17 -O2 -Wall -Wextra -Werror boot_probe.cpp entry.cpp startup2.cpp`: compilou.
- O boot probe validou o retorno do HLE TLS em `0x354DE0`; termina aí, pois o bloco seguinte não foi recompilado.
- `g++ -std=c++17 -O2 -Wall -Wextra -Werror generated.cpp check.cpp`: compilou e o caso testado executou.
- Não foi possível executar os testes diferenciais Unicorn (biblioteca não instalada) nem testar FPS/jogabilidade do jogo.

## Próxima etapa de maior impacto
Para melhorar a experiência *no RPCS3* é necessário medir desempenho real durante a partida por meio de `RPCS3.log.gz`, métricas de FPS/frame time e especificações da CPU/GPU. Para continuar o *port nativo* é necessário recompilar o bloco a partir de `0x354DE0` e validar suas chamadas e seus efeitos.

## Uso
No diretório raiz do projeto:
`python CROSSCHECK.py caminho/para/EBOOT.elf --rpcs3-source caminho/para/rpcs3-0.0.43.zip`
