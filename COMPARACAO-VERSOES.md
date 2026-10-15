# Comparação de executáveis Twisted Metal (BCUS98106)

| Campo | Disco original 1.00 | Novo ELF enviado (provável atualização 1.06) |
| --- | --- | --- |
| SHA-256 | `269642a56f3c70be74df41049876887d07aedd4171ce18a481a05067b1b8564e` | `41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d` |
| Tamanho | 16.306.688 bytes | 16.373.048 bytes |
| Descritor de entrada | `0x00F030D0` | `0x00F13170` |
| Código de entrada | `0x00348DE0` | `0x00354C80` |
| TOC de entrada | `0x00F21930` | `0x00F31AC0` |
| Candidatos a descritores | 14.372 | 14.410 |

O novo arquivo é ELF64 PowerPC big endian e difere do executável do disco. O log do RPCS3 mostra que a sessão jogada usa a atualização 1.06. A associação exata do novo ELF com a atualização depende de confirmar o caminho de origem ao decifrá-lo; a versão não está estabelecida apenas pelo hash do ELF. O hash `PPU-6bb4...` no log é um identificador calculado pelo RPCS3, **não** o SHA-256 do arquivo ELF.

O `elf-map-local.json` que foi enviado junto pertence ao **ELF antigo**: seu `input_sha256` é `269642...`, mesmo hash do executável 1.00. `elf-map-update-1.06.json` foi gerado diretamente do novo arquivo `EBOOT(1).elf` e contém os endereços correspondentes. Esses endereços ainda não são funções decompiladas, nem constituem um jogo recompilado.

## Próxima etapa de engenharia

Confirmar que `EBOOT(1).elf` veio de `dev_hdd0/game/BCUS98106/USRDIR/EBOOT.BIN`, obter perfis de CPU/SPU/GPU durante a fase lenta e identificar funções PPU/SPU responsáveis pela carga. Uma recompilação jogável exigiria implementar a execução PPU, SPU, chamadas do sistema, renderização e leitura dos recursos `.psarc`; os mapas sozinhos não fazem essas tarefas.
