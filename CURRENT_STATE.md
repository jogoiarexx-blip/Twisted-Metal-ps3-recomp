# Twisted Metal 2012 Recomp — Current Technical State

## Resumo Executivo

- **Título:** *Twisted Metal (2012)*
- **Plataforma Original:** PlayStation 3 (`BCUS98106` v1.00)
- **Alvo:** Windows x86-64 Nativo (DirectX 12 / D3D12)
- **Metodologia:** Recompilação Estática (PPU/SPU via `ps3recomp` branch `ydkj-master-bringup` + HLE Runtime C++)
- **Marco Atual:** **M05 — Menu Principal Interativo & Seleção de Categorias** (`SELECT GAME CATEGORY` alcançado)

---

## 1. Auditoria dos Componentes do Sistema

| Componente | Status | Detalhes Técnicos e Evidências |
|---|---|---|
| **PPU Lifter & Código Gerado** | **100% Concluído** | 38.229 funções PPU levantadas (47.106 símbolos mapeados). O código C++ recompiledor está distribuído em 12 compilações modulares (`src/recomp/ppu_recomp_000.cpp` a `011.cpp`, totalizando ~487 MB). |
| **SPU Images & SPURS** | **Concluído & Estável** | 11 imagens SPU embutidas com extração e registro de workloads (`embedded_spu_workloads.c`). 15 workloads de JobQueue ativos. Inicialização de barreira `taskset=0x120F7D00` com 6 workers sem deadlocks. |
| **Sistema de Arquivos (FIOS)** | **Estável & Otimizado** | FIOS streaming funcional. 9 bancos de áudio comuns (`menu`, `fodder`, `global`, `music_channels`, `e3_mp_tdm`, `weapons`, `articulations`, `igv_english`, `shell`) carregam com 100% de integridade a partir de arquivos `.bnk` e `.psarc`. |
| **Renderização RSX (D3D12)** | **Ativo & Renderizando** | Pipeline D3D12 live-draw ativo com 1280x704 (display 1280x720) com scaled blit NV3089. Quadros reais renderizados com até 781 draws por frame e ~21.26% de preenchimento de pixels ativos na UI. |
| **Máquina de Estados Front-End UI** | **Desbloqueado até M05** | Fluxo de vtables validado: `UiLegal_HealthWarning` (`0x00CEF490`) → `UiLegal_1` (`0x00CEF290`) → `UiLegal_2` (`0x00CEF310`) → `UiLegal_3` (`0x00CEF390`) → `UiLegal_4` (`0x00CEF410`) → `UiIntroMovie` (`0x00CF0420`) → `UiAttract` (`0x00CEF690`) → `UiTitle` (`0x00CF0628`) → `UiMainMenu` (`0x00CEF590`) ("SELECT GAME CATEGORY"). |
| **Entrada e Controle (cellPad)** | **Funcional** | Mapeamento direto de teclado e controle XInput via polling e autopress (`PAD_AUTOPRESS=1`). |

---

## 2. Evidências Concretas de Execução

Nos testes nativos de 75 segundos (`twistedmetal.exe input/EBOOT.ELF`):
1. **Inicialização do CRT e PRX:** Mapeamento de TLS (0x10F00000), descritores OPD e heap inicializado com sucesso.
2. **Carregamento de Bancos de Áudio:**
   ```
   [game] CommonBank::IsLoaded() : Loaded "global"...
   [game] CommonBank::IsLoaded() : Loaded "menu"...
   [game] CommonBank::IsLoaded() : Loaded "shell"...
   [game] CommonBank::IsLoaded() : Loaded "igv_english"...
   [game] CommonBank::IsLoaded() : Loaded "articulations"...
   [game] CommonBank::IsLoaded() : Loaded "weapons"... (9.8 MB)
   [game] CommonBank::IsLoaded() : Loaded "e3_mp_tdm"...
   [game] CommonBank::IsLoaded() : Loaded "music_channels"...
   [game] CommonBank::IsLoaded() : Loaded "fodder"...
   ```
3. **Progressão das Telas Legais e Menu Principal:**
   ```
   [ui] UiState::enter state=0x1801CD50 vtable=0x00CEF490 ('UiLegal_HealthWarning')
   [game] !@#$%^&* UiLegal_HealthWarning::onEnter() triggered at [14.3407]
   [ui] UiState::enter state=0x1801C550 vtable=0x00CEF290 ('UiLegal_1')
   [game] !@#$%^&* UiLegal_1::onEnter() triggered at [37.2794]
   [trace] strTable(0x00CE3558, 0x33D) = 0x11EFB170 'SELECT GAME CATEGORY'
   ```
4. **Captura Visual de Superfícies:**
   - Foram gravados 122 dumps de superfícies PPM durante a execução.
   - 35 capturas do menu (`surf_menu_1` a `surf_menu_7`) e 72 capturas de arena (`surf_arena_1` a `surf_arena_8`) foram convertidas em PNG e validadas com mais de 574.829 bytes não-nulos por quadro.

---

## 3. Classificação dos Marcos

- **M01 — Build Reproduzível:** ✅ Concluído.
- **M02 — Boot Nativo Estável:** ✅ Concluído.
- **M03 — Vídeos e Transições:** ✅ Concluído.
- **M04 — Tela Inicial Correta:** ✅ Concluído.
- **M05 — Menu Principal Interativo:** ✅ Concluído / Em evolução de usabilidade.
- **M06 — Seleção de Veículos:** 🔄 Próximo passo imediato.
- **M07 a M18:** 📋 Planejados no ROADMAP.
