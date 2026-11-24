# Análise de Crossfeed: God of War II HD Recomp (GOD_OF_WAR_CROSSFEED.md)

## Visão Geral

O projeto *God of War II HD Recomp* (`andrebrumdev/gow2-recomp` e `sethlikepie/Gow2HD-Windows`) representa uma das implementações de maior maturidade do ecossistema `ps3recomp` para Windows.

---

## 1. Lições Arquiteturais Aproveitadas

1. **Organização Modular do Código Recompilado:**
   - GoW II divide o executável recompiledor em dezenas de unidades `.cpp` menores para permitir compilação paralela com Ninja sem estourar a memória RAM do compilador.
   - *Twisted Metal* adotou essa mesma prática, particionando os 38.229 métodos PPU em 12 compilações (`ppu_recomp_000.cpp` a `011.cpp`), reduzindo o tempo de compilação incremental de minutos para segundos quando apenas o HLE é modificado.

2. **Mitigação de Stack Overflow em Chamadas Reciprocadas:**
   - Em recompilações estáticas de PS3, chamadas convidadas aninhadas traduzem-se em frames de pilha nativos de x86-64.
   - GoW II e Twisted Metal aplicam a flag `/STACK:268435456` (256 MB de pilha para a thread principal) e reserva dinâmica de pilha em `sys_ppu_thread_create`.

3. **Tratamento de Exceções Vetorizadas (VEH):**
   - O runtime do GoW II utiliza manipuladores de exceção vetorial do Windows (`AddVectoredExceptionHandler`) para capturar acessos a ponteiros convidados nulos ou traps do PowerPC sem derrubar o executável.
   - Em Twisted Metal, esse recurso opera ativamente capturando acessos nulos conhecidos do CRT da Sony (`guest read32 from 0x00000004 by func_00348EE8`) e permitindo a continuidade limpa da execução.

4. **Persistência de Shaders D3D12:**
   - A técnica de salvar bytecodes compilados de HLSL/DXBC em disco baseada em hashes de entrada de instrução RSX foi derivada da arquitetura do GoW II, resultando em taxa de acerto instantânea nos runs subsequentes.
