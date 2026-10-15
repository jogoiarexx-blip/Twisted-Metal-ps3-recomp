# Primeiro código PPU recompilado (Twisted Metal BCUS98106)

Este diretório contém **três funções do executável 1.06 traduzidas para C++ de PC** em `generated.cpp`. O arquivo de origem do jogo não está incluído. O `manifest.json` registra o SHA-256 exato do ELF de entrada, endereços e bytes originais. `lift.py` gera novamente o C++ somente se receber o ELF de hash conhecido. A tradução falha explicitamente ao encontrar instruções fora do subconjunto implementado.

| Endereço PPU | Operação observada | Instruções |
| --- | --- | ---: |
| `0x009946C0` | escreve uma palavra de 32 bits em `r3 + 0x11C` | 2 |
| `0x009946E0` | lê uma palavra de 32 bits de `r3 + 0x16C` | 2 |
| `0x00994838` | zera quatro palavras consecutivas no endereço de `r3` | 6 |

O runtime representa registradores e memória em big endian, incluindo checagem de limites. `check.cpp` é um programa de verificação local, não é o jogo.

## Gerar, compilar e testar no Linux

Requisitos: Python 3 com `capstone` e `unicorn`, compilador C++17. A partir deste diretório:

```sh
python3 lift.py /caminho/para/EBOOT-1.06.elf -o generated.cpp
g++ -std=c++17 -O2 -Wall -Wextra -Werror generated.cpp check.cpp -o check
python3 verify.py /caminho/para/EBOOT-1.06.elf
```

A validação executa os **bytes PowerPC originais** em Unicorn no modo PPC32 big endian e compara registradores e memória com o binário C++ nativo. As três funções escolhidas só usam operações de 32 bits; isto não valida operações PPU de 64 bits nem o funcionamento do jogo. Cinco casos passaram no ambiente de desenvolvimento.

No Windows, o `generated.cpp`, `runtime.hpp` e `check.cpp` também podem ser compilados com Visual Studio (`cl /std:c++17 /EHsc /Fe:check.exe generated.cpp check.cpp`) no Developer Command Prompt, ou com `g++`. A compilação para Windows não foi executada neste ambiente.

## Estado real

Este é um ponto de partida de recompilação estática com teste diferencial, **não um executável jogável**. Ainda faltam converter a grande maioria do código PPU, executar SPUs, mapear memória e chamadas PS3, processar arquivos de recursos, entrada, áudio e GPU. O `EBOOT.elf` e o mapa, por si só, não resolvem essas partes. Nenhum aumento de FPS foi medido por esse código.

## Progresso v0.5: início real da inicialização

`entry.cpp` traduz as **oito primeiras instruções** no endereço de entrada `0x00354C80`, até a chamada para `0x00354D88`. `startup2.cpp` traduz as **22 instruções seguintes**, até a chamada `0x00C8D094`. Os geradores `lift_entry.py` e `lift_startup2.py` verificam o SHA-256 e os bytes esperados. O segundo gerador não depende de Capstone.

`boot_probe.cpp` mapeia os segmentos LOAD do ELF 1.06, prepara uma pilha de teste, executa ambos os blocos como C++ nativo e verifica TOC, pilha, LR e uma escrita de memória. O resultado observado neste ambiente foi:

```text
ELF entry 0x354c80 -> first call 0x354d88; TOC 0xf31ac0; SP 0x1ffff90; LR 0x354ca0
Second block 0x354d88 -> call 0xc8d094; SP 0x1fffef0; LR 0x354de0
STOP: target 0xc8d094 is not recompiled yet. Game does not boot.
```

Esse teste executou C++ com os dados do ELF; a comparação diferencial com Unicorn da v0.4 cobre apenas as três funções curtas. O trecho novo foi verificado contra seus bytes e estados esperados, **não** executado em um emulador PPC64 de referência.

No Windows, `COMPILAR-WINDOWS.cmd` tenta compilar `boot_probe.exe` com `cl` ou `g++`; arraste o `EBOOT.elf` da atualização para o arquivo CMD para compilar e executar. Precisa de Visual Studio Developer Command Prompt ou `g++` no PATH. Este pacote não inclui `.exe` de Windows, nem o jogo, e a compilação no Windows ainda não foi testada.

**Correção v0.6:** o log do RPCS3 identifica `0xC8D094` como a importação `sysPrxForUser::sys_initialize_tls` (NID `0x744680A2`). A associação anterior desse ponto com `0x7AA7E0` estava errada e foi removida.

## Progresso v0.6: chamada de TLS

`tls_hle.hpp` implementa um modelo inicial da importação `sys_initialize_tls`: reserva uma área para a thread principal, copia a imagem de `PT_TLS`, zera a parte restante e define `r13`. O teste lê a imagem TLS do ELF e valida cada byte copiado. Para fornecer os argumentos que o carregador PS3 passaria, `boot_probe.cpp` configura `r7` a `r10` a partir do cabeçalho `PT_TLS` e de um ID de thread representativo; **isso é um harness, não uma inicialização completa do carregador PS3**.

Com o ELF enviado, o teste nativo imprimiu `r13=0x03007060` e copiou `0x2B4` bytes. O modelo ainda não implementa mutexes, atexit e demais efeitos da rotina no RPCS3, nem a volta pelo stub `0xC8D094` para continuar o código do jogo. Sem esses componentes, não há menu nem gameplay.

## Progresso v0.7: tabela de importações e retorno

`generate_imports.py` extraiu do log duas sessões idênticas de BCUS98106 v01.06 e deduplicou **583 importações PPU de 35 módulos** em `imports.json` e `import_table.hpp`. A tabela identifica endereço, módulo, NID e nome. `import_dispatch.hpp` resolve `0xC8D094` para `sysPrxForUser::sys_initialize_tls` (NID `0x744680A2`), chama o modelo parcial de TLS e retorna ao endereço de chamada em `0x354DE0`. Para as outras importações, o dispatcher falha explicitamente com o nome da função. Nenhuma é tratada como sucesso silencioso.

O teste compilado chegou a `HLE return PC 0x354de0; import table entries 583`. O trecho seguinte (`0x354DE0`) ainda não foi recompilado. A tabela vem de um log de jogo carregado pelo RPCS3, não substitui uma resolução independente de importações a partir de qualquer ELF ou versão.

## v0.11 — duas importações SPURS modeladas

O `import_dispatch.hpp` passa a resolver `cellSpursBarrierInitialize` (`0x7FDF4FEF`)
e `cellSpursGetTasksetInfo` (`0x9FCB567B`) através de `spurs_hle.hpp`,
com estruturas guest big-endian, checagem de alinhamento e retornos reais de erro.

Teste local: `g++ -std=c++17 -O2 -Wall -Wextra -Werror spurs_hle_test.cpp -o spurs_hle_test && ./spurs_hle_test`.
Isto não acrescenta código PPU além do limite da v0.9 (`0x4EC8D0`), nem
recria SPU, GPU ou um executável de jogo.
