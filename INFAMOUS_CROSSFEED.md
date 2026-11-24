# Integração Tecnológica: Twisted Metal e inFAMOUS: Festival of Blood (INFAMOUS_CROSSFEED.md)

## Visão Geral

Este documento detalha os pontos de contato e a matriz de compartilhamento tecnológico entre dois grandes projetos de recompilação estática de PlayStation 3:
1. **Twisted Metal (2012)** (`BCUS98106` / `d:\Twisted metal`)
2. **inFAMOUS: Festival of Blood** (`NPUA80657` / `D:\infamous recomp`)

---

## 1. Módulos Compartilháveis (Candidatos ao PS3 Recomp Core)

| Subsistema PS3 | Status de Compatibilidade | Estratégia de Compartilhamento |
|---|---|---|
| **PPU Runtime Core** | **100% Compartilhável** | Gerenciamento de memória de 512 MB de espaço de endereço virtual (`vm_base`), conversão big-endian via `__builtin_bswap` e despacho de descritores de funções OPD em 64-bit. |
| **SPURS Policy & Taskset2** | **Compatível com Adaptação** | O sistema de controle de filas SPURS e barreira Taskset2 (`cellSpursBarrierInitialize`) inicializa 6 workers em ambos os jogos. Ajustes na alocação de prioridades de threads podem ser unificados. |
| **D3D12 RSX Presentation & Fences** | **Compatível com Adaptação** | A série 0013 de *Festival of Blood* introduz retenção de buffers até a fence D3D12 ser liberada pela GPU. Esse mecanismo evita tearing e falhas de alocação de recursos em *Twisted Metal*. |
| **SPU Cache Expansion** | **Diretamente Aplicável** | A expansão do cache SPU de 8 para 64 entradas adotada no Festival of Blood com hashing de integridade antes do hit de cache previne recompilação redundante em tempo de execução. |
| **HLE de cellPad / Input** | **100% Compartilhável** | Mapeamento de teclado e XInput com suporte a autopress e buffers circulares. |
| **Ferramentas de Análise PPU e SPU** | **Diretamente Aplicável** | Os utilitários em `repo_git/tools/`: `analyze_ppu.py`, `compare_spu_modules.py` e `diagnose_spurs_dma_loop.py` operam diretamente sobre qualquer binário ELF de PS3. |

---

## 2. Componentes Exclusivos (Não Compartilháveis)

- **Motor de Áudio BoomRangBuss (ESP / Twisted Metal):** Exclusivo do Twisted Metal; utiliza comunicação de anel com a thread host e rotinas de ducking de áudio específicas.
- **Motor Sucker Punch (Festival of Blood):** O motor de inFAMOUS possui alocadores de blocos de memória e carregamento de streaming de pacotes proprietários que não se aplicam ao Twisted Metal.

---

## 3. Próximos Passos de Integração

1. Portar a política de retenção de fences D3D12 (`0013`) de Festival of Blood para aprimorar a estabilidade de quadros longos no Twisted Metal.
2. Unificar a ferramenta `analyze_ppu.py` para detecção de stubs PPU não resolvidos.
