> **v0.11:** novo [CROSSFEED-v0.11-SPURS.md](CROSSFEED-v0.11-SPURS.md), com dois NIDs SPURS de pós-FX ligados ao dispatcher e testes de memória big-endian. **Ainda não inicializa o jogo.**

> **v0.9:** veja [EVOLUCAO-v0.9.md](EVOLUCAO-v0.9.md) para o novo bloco PPU, testes e limitações.

# Twisted Metal (BCUS98106) — análise dos executáveis

Este pacote contém somente ferramentas e resultados de análise. Não contém o jogo nem um port executável.

**Versões:** `elf-map.json` mapeia o executável do disco 1.00. `elf-map-update-1.06.json` mapeia o novo `EBOOT(1).elf` enviado, possivelmente o executável da atualização 1.06 que o log mostra em uso. Consulte `COMPARACAO-VERSOES.md` e `RELATORIO-LOG.md`.

## Arquivos identificados

- `PARAM.SFO`: Twisted Metal, BCUS98106, versão de disco 01.00.
- `EBOOT.BIN`: SELF de 16.309.120 bytes; SHA-256 `367ab214d106211b9c30767b302d1698c036254a653747cb02615c879d242373`.
- `EBOOT.elf`: ELF64 PowerPC big endian, sem símbolos; SHA-256 `269642a56f3c70be74df41049876887d07aedd4171ce18a481a05067b1b8564e`. O mapa completo consta em `elf-map.json`. O novo `EBOOT(1).elf` tem SHA-256 `41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d` e seu mapa está em `elf-map-update-1.06.json`.

O campo de entrada do ELF (`0x00F030D0`) contém um descritor PPU com endereço de código `0x00348DE0` e TOC `0x00F21930`. Executar bytes no endereço do descritor seria um erro.

## Reproduzir o mapa

No Windows, execute `ANALISAR-WINDOWS.cmd`, arraste `EBOOT.elf` para a janela e pressione Enter. O resultado sera salvo em `elf-map-local.json` sem precisar instalar Python. O arquivo `elf-map.json` ja contem o resultado do ELF enviado.

Tambem e possivel usar Python 3:

```cmd
py -3 tools\map_elf.py EBOOT.elf -o elf-map-local.json
```

O programa lê o ELF localmente e produz endereços, segmentos e candidatos a descritores de função. Ele não altera o ELF e não exige arquivos de fases. O campo `descriptor_count` é contagem de candidatos, não prova de funções recompiladas.

## Próximo marco técnico

O ELF novo foi mapeado. O próximo passo é confirmar sua origem na pasta da atualização, fazer perfil da fase lenta e estudar fluxo de controle, chamadas do sistema e tarefas SPU; os endereços gerados não são um port jogável.

## Primeira implementação de recompilação estática

A pasta `recomp/` contém o primeiro código C++ gerado de três funções PPU do novo ELF, seu gerador restrito e uma comparação com execução PowerPC. Leia `recomp/README.md` para endereços, comandos e limites. Este trabalho ainda não executa o jogo.

### Inicialização (v0.5)

A pasta `recomp/` agora traduz 30 instruções consecutivas desde a entrada PPU e executa os dois blocos com os segmentos reais do ELF até `0xC8D094`. Consulte `recomp/README.md` e use `recomp/COMPILAR-WINDOWS.cmd` se houver compilador C++ instalado. Ainda não inicializa o jogo.

### Importação TLS (v0.6)

O primeiro destino `0xC8D094` é `sys_initialize_tls`. O harness em `recomp/` contém uma implementação parcial de TLS e verifica a cópia de `PT_TLS`. Essa etapa ainda não inicializa o jogo.

### Dispatcher de importações (v0.7)

Os arquivos `recomp/imports.json`, `recomp/import_table.hpp` e `recomp/import_dispatch.hpp` descrevem 583 importações PPU vistas no log da sessão e retomam a execução depois do HLE parcial de `sys_initialize_tls`, em `0x354DE0`. As demais importações ainda não têm implementação. O jogo não abre nesta versão.
