# Twisted Metal v0.18 — Decompilação do Helper de Arena PPU (0x988AA8)

**Base:** BCUS98106, EBOOT associado à atualização 1.06 (SHA-256: `41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d`).
Este repositório contém ferramentas de análise, código estaticamente recompilado e testes limpos (clean-room); **não contém o jogo**.

## Resultado

O boot probe local com o EBOOT real do usuário avançou além do ponto pendente em `0x988AA8` e alcançou a fronteira da sub-rotina de free-list em **`0x988314`**.

```text
ELF entry 0x354c80 -> first call 0x354d88; TOC 0xf31ac0; SP 0x1ffff90; LR 0x354ca0
Second block 0x354d88 -> call 0xc8d094; SP 0x1fffef0; LR 0x354de0
HLE sys_initialize_tls: r13 0x3007060; copied 0x2b4 bytes at 0x3000060
HLE return PC 0x354de0; import table entries 583
Third block 0x354de0 -> call 0x4ec8d0; LR 0x354e58
Memory setup 0x4ec8d0 -> LV2 syscall 0x160 at PC 0x4ec8ec; arg 0x17dfc48
LV2 0x160: total 0xd500000 available 0xd500000
LV2 0x15c: allocated guest 0x40000000 (0xF00000 bytes, 1MB pages)
Heap allocation 0x98c8c0 -> init helper 0x988b78
Allocator descriptor initialized; memset at 0x98769c
Heap header ready; list-head helper at 0x988b0c
Arena block header initialized and tagged; helper 0x988aa8 returned
NEXT: helper 0x988314 (free-list node insertion, NOT recompiled). No menu or gameplay yet.
```

## Análise e Recompilação de `0x988AA8`

A função em `0x988AA8` (100 bytes, 25 instruções PowerPC) é o helper de alinhamento e inicialização da arena de memória:
- **Alinhamento da Arena:** Calcula o padding necessário para alinhar a arena em limites de 16 bytes (`(r4 + 8) & 0xF`).
- **Ajuste de Dimensões:** Subtrai o padding do tamanho livre e grava o tamanho ajustado no descritor (`r3 + 12`).
- **Tagging de Bloco:** Marca o bloco de arena inicial com a flag de ocupado/guarda (`size | 1`) no offset `+4`.
- **Link do Final da Arena:** Calcula o limite final da arena e grava o ponteiro de ligação no bloco final.
- **Máscara do Alocador:** Lê a máscara configurada no descritor global do alocador e armazena em `r3 + 28`.
- **Retorno:** Retorna via `blr` para o endereço de chamada em `0x98C9C8`.

## Região de Código Verificada

Fixada em `recomp/verify_heap_init.py`:
- Intervalo: `0x988AA8` .. `0x988B0C` (100 bytes)
- SHA-256 dos bytes PowerPC: `10f77ca3f68f5dafadcff8226808ebb862914b3ddd0a94d244cd5666bd1646c8`

## Como Reproduzir no Windows / Linux

```bash
cd recomp
python verify_heap_init.py /caminho/para/EBOOT.elf
g++ -std=c++17 -O2 -Wall -Wextra heap_init.cpp heap_init_test.cpp -o heap_init_test.exe
./heap_init_test.exe
g++ -std=c++17 -O2 -Wall -Wextra entry.cpp startup2.cpp startup3.cpp startup4.cpp heap_init.cpp boot_probe.cpp -o boot_probe.exe
./boot_probe.exe /caminho/para/EBOOT.elf
```

## Próximos Passos (Milestone v0.19)

1. Decompilar e mapear a função `0x988314` (inserção e validação do nó de free-list no alocador).
2. Concluir a cadeia de inicialização do alocador para retornar com sucesso para `0x4EC92C`.
3. Prosseguir a execução da sequência `startup4` até os subsistemas seguintes do motor TMX (GpuManager, SPURS e TaskManager).
