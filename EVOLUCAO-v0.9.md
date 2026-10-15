# Twisted Metal BCUS98106 1.06 — v0.9 startup continuation

## O que mudou de verdade
- Acrescentado `recomp/startup3.cpp`, tradução nativa C++ do bloco PPC `0x00354DE0` a `0x00354E54`, inclusive as duas rotinas de cópia de memória com comparações PPC de 64 bits e atualização de registradores.
- O fluxo do harness agora continua da importação TLS até a próxima chamada `0x004EC8D0`, com `LR=0x00354E58`.
- Acrescentado `verify_startup3.py` para checar SHA-256 do EBOOT exato e as 30 palavras de instruções.
- Acrescentado `startup3_test.cpp`: 16 casos para os loops com contagens de 0, 1, 3 e 9.
- Atualizado o CMD de compilação do Windows para incluir o novo arquivo.

## Testado no ambiente Linux
- `python3 recomp/verify_startup3.py /mnt/data/EBOOT.elf`: passou, 30 instruções.
- `g++ -std=c++17 -O2 -Wall -Wextra -Werror recomp/startup3.cpp recomp/startup3_test.cpp -o startup3_test && ./startup3_test`: passou, 16 casos.
- `g++ -std=c++17 -O2 -Wall -Wextra -Werror recomp/entry.cpp recomp/startup2.cpp recomp/startup3.cpp recomp/boot_probe.cpp -o boot_probe && ./boot_probe /mnt/data/EBOOT.elf`: passou, avançou para `0x4EC8D0`.
- Compilação Windows, FPS e gameplay: NÃO testados.

## Limitações
- Trata-se de uma recompilação experimental de blocos PPU. O jogo não inicia nem é jogável como aplicativo nativo.
- Ainda não foi feita validação diferencial de **todo** o novo bloco frente a um emulador PPC64; testes cobrem bytes e estados selecionados em C++.
- Os testes de cópia possuem um limite de segurança de iterações no harness, não presente na máquina PS3.
- Sem melhorias medidas no RPCS3. O próximo alvo identificado é a chamada `0x4EC8D0`.

## Comandos
Na pasta `recomp`, com compilador C++17:
```
python3 verify_startup3.py /caminho/EBOOT.elf
g++ -std=c++17 -O2 -Wall -Wextra -Werror startup3.cpp startup3_test.cpp -o startup3_test
./startup3_test
g++ -std=c++17 -O2 -Wall -Wextra -Werror entry.cpp startup2.cpp startup3.cpp boot_probe.cpp -o boot_probe
./boot_probe /caminho/EBOOT.elf
```
