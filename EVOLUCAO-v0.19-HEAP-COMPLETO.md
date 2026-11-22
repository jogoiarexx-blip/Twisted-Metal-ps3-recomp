# Twisted Metal v0.19 — Inicialização Completa do Heap e Retorno ao Motor (0x354E58)

**Base:** BCUS98106, EBOOT associado à atualização 1.06 (SHA-256: `41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d`).
Este repositório contém apenas ferramentas, código limpo recompilado e testes; **não contém o jogo**.

## Resultado

O boot probe local executou com o EBOOT real de ponta a ponta e concluiu **toda a inicialização do subsistema de memória (LV2 + Alocador TMX Heap)**, retornando com sucesso para o fluxo principal de inicialização do motor em **`0x00354E58`**.

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
Free-list node registered; helper 0x988314 returned
Heap initialization complete! Returned to startup4 at 0x4ec92c (descriptor: 0x40000010)
Memory subsystem initialized; stored to 0x017DFC44; returned to 0x354e58
NEXT: engine subsystem constructors at 0x354e58 (GpuManager, SPURS, TaskManager). No menu or gameplay yet.
```

## Rotinas Decompiladas nesta Versão

1. **`heap_helper_00988314` (140 bytes, 35 instruções PPC):**
   - Cria frame de 144 bytes e salva `r29..r31` e `lr`.
   - Consulta a lista circular de nós de blocos livres (`0x0098828C`).
   - Retorna `0` para lista vazia/nova arena e salta diretamente para o epílogo em `0x0098837C`.
   - Restaura a pilha e retorna `1` em `r3` para indicar nó registrado com sucesso.
2. **`heap_after_00988314` (em `0x0098C9D4`):**
   - Despacha a importação `sys_lwmutex_create` (NID `0x2F85C0EF` no endereço `0x00C8CE64`) para proteger o alocador com um mutex leve.
   - Executa o epílogo do heap em `0x0098C9F8`: restaura `r25..r31`, devolve o descritor em `r3` e retorna para `0x004EC92C`.
3. **`startup_after_heap_init` (em `0x004EC92C`):**
   - Grava o ponteiro do descritor do heap no endereço estático global do jogo: `0x017DFC44`.
   - Executa a chamada no-op `0x004ED1F0`.
   - Desempilha o frame de 112 bytes de `startup4` e retorna para `0x00354E58`.

## Regiões PPC Fixadas em verify_heap_init.py

- `0x98c8c0`..`0x98c954`: `d0eff769e237e0ab4936226ba7a75ab6655195cc9d6cac35dd7f728f7aa3ca98`
- `0x988b78`..`0x988be8`: `ef9fa0567ab2b10124194a11d6428be21879f9fb064a934e97e85592ff859b49`
- `0x988aa8`..`0x988b0c`: `10f77ca3f68f5dafadcff8226808ebb862914b3ddd0a94d244cd5666bd1646c8`
- `0x988314`..`0x9883a0`: `33b13cc337d7e773f85a9f83b92f1779904fff590938fae94177f8190f3eedec`

## Próximo Alvo (Milestone v0.20)

Em **`0x00354E58`**, o motor inicia a instanciação dos subsistemas globais:
- Construtor do `TaskManager` e despachante de tarefas por quadro.
- Inicialização do subsistema de gráficos e contexto GCM.
- Configuração do SPURS e instâncias de tarefas.
