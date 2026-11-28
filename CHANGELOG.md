# Registro de Alterações (CHANGELOG.md)

Todas as alterações notáveis no projeto *Twisted Metal (2012) Static Recompilation* estão registradas neste arquivo.

---

## [Unreleased] - 2026-11-28

### Adicionado
- **Relatório de Status First Playable (`FIRST_PLAYABLE_STATUS.md`):** Consolidada avaliação técnica de `TM-01` a `TM-09` com métricas de FPS, evidências de renderização e diagnóstico do bloqueio de geometria 3D (`func_00645708` / `[jq-cull]`).
- **Patch consolidado do runtime (`patches/0002-ps3recomp-tm-bringup-and-fp-fix.patch`):** Exportado diff completo de `ps3recomp` com melhorias de `rsx_live_draw.c`, `rsx_fp_decompiler.c`, `rsx_vp_decompiler.c`, `rsx_commands.c`, `cellPad.c`, `cellSpurs.c` e `spu_workload.c`.

### Corrigido
- **Borramento vertical / Ghosting no Menu e Garagem:** Identificada a causa raiz no pass pós-FX `f81da28d` (`0x1870000:E5` lido sem depth-alias packing) e restaurado `lerp(...)` em `rsx_fp_decompiler.c`, recuperando nitidez total nas capturas de Menu e Story/Garage (`nonblack=244450`).
- **Queda severa de FPS com logs redirecionados:** Identificado que `ps3_log_verbose()` ativava logs massivos em redirecionamento de `stderr`; com `PS3_VERBOSE=0` o fluxo Menu → Story/Garage opera entre `34.3` e `55.4 FPS`.

---

## [Unreleased] - 2026-11-24

### Adicionado
- **Progressão Completa para o Menu Principal:** Implementado auto-avanço das telas de aviso legal (`UiLegal_HealthWarning` a `UiLegal_4`), tela de atração (`UiAttract`) e tela de título (`UiTitle`) diretamente para `UiMainMenu` (`0x00CEF590`), alcançando `"SELECT GAME CATEGORY"`.
- **Mapeamento de Vtables Front-End:** Mapeadas e catalogadas 11 tabelas virtuais principais do gerenciador de interface em `src/hle_extra.cpp`.
- **Captura Periódica de Telas da UI:** Adicionado dump automático de superfícies a cada 150 frames em `src/boot_main.cpp` (`surf_menu_%d_%08X.ppm`).
- **Documentação de Auditoria Completa:** Criados `CURRENT_STATE.md`, `REUSE_MATRIX.md`, `INFAMOUS_CROSSFEED.md`, `GOD_OF_WAR_CROSSFEED.md`, `REA_ANALYSIS.md`, `RPCS3_DIFF.md`, `RECOMP_COVERAGE.md`, `BUILD_MANIFEST.json`, `KNOWN_BUGS.md` e `ROADMAP.md`.

### Corrigido
- **Corrupção de Fila FIOS:** Removida a limpeza acidental de `s + 0x220` em `tm_brb_ack_tick`, restaurando o carregamento dos 9 bancos de áudio comuns (`menu`, `fodder`, `global`, `music_channels`, `e3_mp_tdm`, `weapons`, `articulations`, `igv_english`, `shell`) sem stalls.
- **Preempção Indevida no Runner:** Corrigido valor padrão de `TM_FORCEWORLD` em `tools/runner.py`, prevenindo a interrupção prematura da máquina de estados Front-End antes da carga dos recursos do menu.
- **Escala de Timers Legais:** Adicionada aceleração automática em `func_005CAEA0` (`UiState::setTimer`) de 5.0s para 0.4s por tela.
