# Análise Diferencial contra o RPCS3 (RPCS3_DIFF.md)

## Visão Geral

O emulador RPCS3 é utilizado como oráculo comportamental de validação de referência para *Twisted Metal* (`BCUS98106`), permitindo comparar com precisão os pontos de divergência em tempo de inicialização, E/S de arquivos e sincronização RSX.

---

## 1. Tabela de Comparação de Comportamento

| Aspecto | Execução Nativa (Twisted Metal Recomp) | Execução RPCS3 (Referência) | Análise Técnica |
|---|---|---|---|
| **Tempo de Boot para First Draw** | **< 1.0 segundo** | ~3.5 segundos | Recompilação estática x86-64 direta elimina sobrecarga de compilação JIT de PPU e SPU em tempo real. |
| **Streaming de Arquivos FIOS** | **Síncrono/Assíncrono via Host IO** | Virtualizado em VFS | Ambas as versões leem 9 arquivos `.bnk` no diretório `audio/globals/`. O Recomp processa arquivos em chunks de 32 KB idênticos ao hardware original. |
| **Sincronização SPURS Taskset2** | **6 workers nativos de thread** | 6 threads SPU de emulador | A barreira `0x120F9600` atinge sincronização estável em ambos os ambientes sem deadlocks. |
| **Resolução de Renderização RSX** | **1280x704 com blit 1280x720** | 1280x720 nativo | O jogo renderiza originalmente internamente a 1280x704 com margens de overscan de 8 linhas. No Recomp D3D12, o blit NV3089 realiza a escala proporcional exata. |
| **Progressão de Telas Legais** | **Acelerada para 0.4s por tela** | ~5.0s por tela | O Recomp implementa escala de timers para fins de desenvolvimento ágil (`TM_FAST_LEGAL=1`). |
| **Entrada no Menu Principal** | **Alcançado (`SELECT GAME CATEGORY`)** | Alcançado | A máquina de estados atinge a mesma vtable de destino `0x00CEF590` e carrega a tabela de strings em `0x11EFB170`. |

---

## 2. Princípios de Não-Contaminação de Código

- Não há importação de código GPL do RPCS3 para a base de código do Recomp (MIT).
- Todas as implementações de HLE e hooks baseiam-se em reverse engineering limpo das funções do executável PS3 e nas especificações de API de bibliotecas abertas.
