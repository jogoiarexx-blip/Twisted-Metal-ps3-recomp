# Twisted Metal 2012 Recomp — Status Atual (Operação First Playable)

**Data da análise:** 2026-11-28  
**Alvo:** `BCUS98106` v1.00 (`PS3_GAME\USRDIR\EBOOT.elf`) — Windows x86-64 Nativo (D3D12)  
**Branch atual:** `diag/uiattract-status`

---

## 1. Resumo por Checkpoint (`TM-01` a `TM-09`)

| Checkpoint | Status | Nota (0–10) | Evidência e Situação Atual |
|---|---|---|---|
| **TM-01 — Inicialização completa** | ✅ Concluído | **9/10** | Boot nativo completo (`OPD 0x00F030D0`), PRX/TLS, SPURS (11 imagens SPU, 15 workloads), FIOS carregando os 9 bancos de áudio comuns. |
| **TM-02 — Menu principal original** | ✅ Concluído | **9/10** | `UiMainMenu`, telas de aviso, título e fundo renderizados de forma nítida após correção do borramento vertical. |
| **TM-03 — Controles e navegação** | ✅ Funcional | **8/10** | Navegação `cellPad` (teclado / XInput) funcional pelos menus, seleção de dificuldade e telas de confirmação. |
| **TM-04 — RSX e shaders** | 🔄 Em progresso | **6/10** | Pipeline D3D12 `rsx_live_draw.c` ativo (1280x704 → 1280x720 via `NV3089`). UI Scaleform e pós-FX 2D nítidos; pendente renderização de geometria 3D de cena (`DRAW_INDEX_ARRAY`). |
| **TM-05 — Seleção de modos** | ✅ Concluído (Offline) | **8/10** | Fluxo `ONE PLAYER` → `STORY` → `STORY SAVED GAMES` (`SELECT A GAME`, `NORMAL`) → `GARAGE` → `START EVENT` funcional. |
| **TM-06 — Seleção de veículos** | ⚠️ Parcial | **4/10** | UI 2D da Garagem funciona e permite iniciar evento, porém os veículos 3D não aparecem (mesmo bloqueio de cena 3D em `func_00645708`). |
| **TM-07 — Carregamento da primeira fase** | ⚠️ Parcial | **4/10** | Streaming de `suburbs.psarc` e transição para `Sunsprings CALIFORNIA` acontecem, mas a arena 3D ainda não emite batches de geometria (`last_draws=2..3`). |
| **TM-08 — Primeiro gameplay funcional** | ⏳ Pendente | **1/10** | Bloqueado pela ausência de geometria 3D / visibilidade de cena (`TM-06` / `TM-07`). |
| **TM-09 — Desempenho e estabilidade** | 🔄 Parcial | **6/10** | Com `PS3_VERBOSE=0`, o runtime atinge `34.3–55.4 FPS` no fluxo Menu → Story/Garage (contra ~10 FPS com logging verboso em `stderr` redirecionado). |

---

## 2. Melhorias Recentes Aplicadas e Verificadas

1. **Correção do borramento / ghosting vertical no Menu e na Garagem (`rsx_fp_decompiler.c`):**
   - O pass fullscreen `f81da28d` (`d=187` no Menu / `6dd0c4e9` na Garagem) lê `0x1870000:E5` (depth buffer aliased como `A8R8G8B8`) e distorce o frame anterior (`0x1190000`).
   - Como `0x1870000` recebia apenas clear de depth (`#clear mask=0x03`), a leitura como cor retornava `(0,0,0)` (`Z=0.0`), disparando o feedback vertical de `+100px`.
   - Restaurado o comportamento `lerp(...)` em `rsx_fp_decompiler.c` (registrado em `patches/0002-ps3recomp-tm-bringup-and-fp-fix.patch`), eliminando o borramento e deixando Menu (`frame_000120`/`160`) e Story/Garage (`frame_000280`, `nonblack=244450`) 100% nítidos.
2. **Diagnóstico do gargalo de FPS por logging (`PS3_VERBOSE=0`):**
   - `ps3_log_verbose()` em `ps3recomp/runtime/ps3_log.h` ativa logging massivo automaticamente quando `stderr` é redirecionado, gerando centenas de milhares de linhas `[spurs-job]` / `[cellNetCtl]` / `[RSX null]` com contenção em lock de arquivo.
   - Executando com `PS3_VERBOSE=0`, a taxa sobe para `55.4 FPS` (frames `1..278`), `43.9 FPS` (`278..498`), `38.8–44.1 FPS` (`552..967`) e `34.3 FPS` (`967..1140`).
3. **Mapeamento exato do bloqueio de geometria 3D (`TM-06` / `TM-07`):**
   - Identificado `func_00645708` (`ppu_recomp_003.cpp`) como o pass principal da cena 3D (leitura de `numVisible` em `r1+0x378`, `r1+0x384`, `r1+0x388` e escrita de `NV4097_DRAW_INDEX_ARRAY` / `SET_INDEX_ARRAY_DMA` em `0x01A222C0`).
   - Próximo passo técnico direto: investigar `func_00642BA0`, flags de visibilidade/`[jq-cull]` (`0x019307D0`) e `TM_POOL_NOWAIT` para liberar a renderização 3D dos veículos e da arena Sunsprings.
