# Integração dos Upstreams: sp00nznet e FranklinCG

Este documento detalha como os dois projetos públicos de referência para **Twisted Metal (2012) PS3** foram integrados para acelerar a recompilação e decompilação do projeto:

1. **sp00nznet/twistedmetal** (`https://github.com/sp00nznet/twistedmetal`)
2. **franklincg/twisted-metal-2012-ps3-native-port** (`https://github.com/franklincg/twisted-metal-2012-ps3-native-port`)

---

## 1. O que foi integrado do sp00nznet/twistedmetal

### Ferramentas de Pipeline (`tools/`):
* **`unpsarc.py`**: Extrator de arquivos `.psarc` com suporte a `contents.dat` e descompressão de membros para montagem no sistema FIOS.
* **`recarve_spu.py`**: Ajuste e extração de imagens SPU embutidas no executável com base na extensão de tamanho do runtime.
* **`symbolize.py`**: Conversão de RVAs de watchdog de crash de volta para nomes e endereços de funções convidadas (PPU).
* **`seed_gaps.py`**: Varredura de intervalos não levantados entre funções conhecidas no executável.
* **`post_lift.py`**: Patches pós-lifter idempotentes para o código C++ gerado.

### HLE e Subsistemas Críticos (`integration/upstream/` e `recomp/`):
* **Descoberta do FIOS `sys_ppu_thread_once` (NID `0xA3E3BE68`)**:
  * O agendador de arquivos FIOS do motor do jogo inicializa mutexes e variáveis de condição dentro de um `sys_ppu_thread_once`. Se essa rotina não for tratada, os ponteiros de mutex permanecem zerados e o jogo trava aguardando `fios worker cond`.
  * Implementado em [sysprx_hle.hpp](file:///d:/Twisted%20metal/recomp/sysprx_hle.hpp) e registrado no despachante de NIDs.
* **Registro de Bibliotecas Estáticas `sys_prx_register_library` (NID `0x42B23552`)**:
  * Confirma registro das exportações do engine com o loader.
* **Mapeamento de GPU RSX `cellGcmMapEaIoAddressWithFlags` (NID `0x626E8518`)**:
  * Mapeamento de memória efetiva para endereços de I/O do RSX GCM.
* **Descompressor In-Engine**:
  * `tm_inflate.cpp` integrado e testado com suíte de testes sintéticos.
* **Referência de HLE Completa**:
  * `hle_extra_reference.cpp` (2.222 linhas de implementações HLE testadas no boot do Twisted Metal) e referências de vídeo `vdec_hle_reference.cpp` / `vdec_mf_reference.cpp`.

---

## 2. O que foi integrado do franklincg/twisted-metal-2012-ps3-native-port

### Contratos e Estruturas de Dados do Engine:
* **`contracts/taskset_layout.json`**:
  * Contrato formal do layout da estrutura SPURS Taskset do FranklinCG / TMX Engine (limite de 128 tarefas, extensão de 6.400 bytes, campos de `RUNNING`, `READY`, `ENABLED`, etc.).
* **Testes de Regressão SPURS**:
  * `franklin_taskset_probe.c` validando manipulação de bitsets de tarefas em big-endian.

---

## 3. Matriz de Compatibilidade: Disco 1.00 vs Update 1.06

| Recurso | Disco 1.00 (sp00nznet) | Update 1.06 (Local / Probe) |
|---|---|---|
| **EBOOT SHA-256** | `fcae7fe5...` | `41a8aae2...` |
| **PPU TOC** | `0xF21930` | `0xF31AC0` |
| **Entrada PPU** | `0x00354C80` | `0x00354C80` |
| **Heap Arena** | `0x98C8C0` | `0x98C8C0` |
| **SPU Images** | 11 embutidas + 15 JQ capturadas | 11 embutidas no ELF |
| **Status Atual** | Scripts de pipeline prontos | Boot probe passou por `0x988AA8` até `0x988314` |

---

## 4. Como Executar Todos os Testes

```bash
# Testes Python do pipeline
python integration/native/test_native.py
python integration/native/test_prepare_lift.py
python integration/upstream/test_elf_version.py

# Testes C++ do recompilador
cd recomp
g++ -std=c++17 -O2 -Wall -Wextra sysprx_hle_test.cpp -o sysprx_hle_test.exe
./sysprx_hle_test.exe
./lv2_memory_test.exe
./heap_init_test.exe
./spurs_hle_test.exe

# Boot probe com EBOOT real
./boot_probe.exe ../BCUS98106/USRDIR/EBOOT.elf
```
