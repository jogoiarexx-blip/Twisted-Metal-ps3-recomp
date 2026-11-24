# Cobertura de Recompilação (RECOMP_COVERAGE.md)

## Métricas Gerais

- **Binário Original:** `BCUS98106` v1.00 (`EBOOT.BIN` / `EBOOT.ELF`)
- **Arquitetura Convidada:** PowerPC 64-bit (Cell PPU) + Synergistic Processing Elements (Cell SPU)
- **Tamanho do Código Executável:** ~13 MB de código binário `.text`
- **Total de Funções PPU Identificadas:** **38.229 funções**
- **Total de Símbolos Mapeados:** **47.106 símbolos**
- **Funções PPU Recompiladas (C++ Nativo):** **38.229 (100.0% do conjunto identificado)**

---

## 1. Distribuição dos Chunks de Código Recompilado

| Arquivo Fonte | Tamanho em Disco | Símbolos Mapeados Aproximados |
|---|---|---|
| `src/recomp/ppu_recomp_000.cpp` | ~44.5 MB | ~3.900 |
| `src/recomp/ppu_recomp_001.cpp` | ~42.7 MB | ~3.800 |
| `src/recomp/ppu_recomp_002.cpp` | ~42.5 MB | ~3.750 |
| `src/recomp/ppu_recomp_003.cpp` | ~35.9 MB | ~3.150 |
| `src/recomp/ppu_recomp_004.cpp` | ~35.8 MB | ~3.150 |
| `src/recomp/ppu_recomp_005.cpp` | ~38.2 MB | ~3.350 |
| `src/recomp/ppu_recomp_006.cpp` | ~40.6 MB | ~3.550 |
| `src/recomp/ppu_recomp_007.cpp` | ~44.3 MB | ~3.900 |
| `src/recomp/ppu_recomp_008.cpp` | ~40.5 MB | ~3.550 |
| `src/recomp/ppu_recomp_009.cpp` | ~47.5 MB | ~4.150 |
| `src/recomp/ppu_recomp_010.cpp` | ~50.4 MB | ~4.400 |
| `src/recomp/ppu_recomp_011.cpp` | ~20.7 MB | ~1.850 |
| **Total C++ Gerado** | **~487.7 MB** | **47.106 símbolos** |

---

## 2. Cobertura SPU e Workloads

- **Imagens SPU Extraídas e Compiladas:** 11 imagens embutidas em `embedded_spu_workloads.c`.
- **Jobs de JobQueue SPURS:** 15 workloads registrados com despacho por hash de fingerprint e rotinas estáticas.
- **Fallbacks HLE Implementados:** 100% dos stubs de inicialização de CRT, PRX e subsistemas de I/O requeridos pelo boot estão presentes em `src/hle_extra.cpp` e `src/gen/ppu_hle_nids.cpp`.
