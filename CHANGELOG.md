# Registro de Alterações (CHANGELOG.md)

Todas as alterações notáveis no projeto *Twisted Metal (2012) Static Recompilation* estão registradas neste arquivo.

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
