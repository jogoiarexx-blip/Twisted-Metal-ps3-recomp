# Twisted Metal 2012 Recomp — Known Bugs and Root Cause Analysis

## Status Atual dos Bloqueios Conhecidos

Este documento registra o inventário técnico de bugs, stubs, comportamentos anômalos investigados e suas respectivas soluções no projeto de recompilação estática de *Twisted Metal* (2012, `BCUS98106`).

---

### 1. [RESOLVIDO] Corrupção da Fila do Scheduler FIOS durante Startup

- **Sintoma:** Carregamento travava no frame 389, gerando loop infinito de `[cellMsgDialog] Abort()`.
- **Causa Raiz:** Um hack experimental em `tm_brb_ack_tick` (`src/hle_extra.cpp`) realizava escrita de `vm_write32(s + 0x220, 0)` em todos os schedulers FIOS a cada frame. Isso zerava o contador de requisições pendentes enquanto o streaming de arquivos `.bnk` ainda estava ativo.
- **Solução:** Removida a limpeza de `s + 0x220` durante a execução normal e restrita exclusivamente ao encerramento do processo (`func_0036204C`).
- **Status:** **Resolvido**. Todos os 9 bancos de áudio (`menu`, `fodder`, `global`, `music_channels`, `e3_mp_tdm`, `weapons`, `articulations`, `igv_english`, `shell`) carregam com 100% de integridade.

---

### 2. [RESOLVIDO] Preempção Indevida da Máquina de Estados pelo Runner

- **Sintoma:** O jogo não progredia para além da tela de aviso de saúde quando executado via `runner.py`.
- **Causa Raiz:** `tools/runner.py` injetava por padrão `TM_FORCEWORLD="5,menu"`. No 5º segundo de execução, a rotina `tm_force_world` invocava `func_0010EC08(mgr)` para forçar recarga de mundo, interrompendo o ciclo natural da máquina de estados UI antes do término da carga dos bancos comuns (que leva ~12s).
- **Solução:** Ajustado `tools/runner.py` para não injetar `TM_FORCEWORLD` por padrão, permitindo que a máquina de estados UI execute todas as telas legais e entre em `UiTitle` e `UiMainMenu`.
- **Status:** **Resolvido**.

---

### 3. [RESOLVIDO] Timers de Telas Legais Excessivamente Longos

- **Sintoma:** Cada tela de aviso legal levava de 5 a 10 segundos para avançar, totalizando quase 1 minuto apenas para passar avisos estáticos.
- **Causa Raiz:** O jogo original programa durações de 5.0f segundos em ponto flutuante big-endian no offset `+0x80` / `+0x84` de cada objeto de estado.
- **Solução:** Implementado hook `func_005CAEA0` (`UiState::setTimer`) que intercepta valores float entre 1.0f e 15.0f e escala-os para `0.4f` segundos quando `TM_FAST_LEGAL=1` (padrão).
- **Status:** **Resolvido**. As 5 telas legais avançam fluidamente em ~2 segundos.

---

### 4. [EM ANDAMENTO] Simulação de Input Pad em `UiTitle` ("Press START")

- **Sintoma:** Na tela de título ("Press START"), o jogo requer o envio do evento de botão START do jogador 1 para desbloquear o menu principal.
- **Causa Raiz:** O loop de eventos UI processa o buffer de entrada através de `fe_mgr + 0x30`.
- **Solução Atual:** Auto-avanço temporizado após 60 ticks em `UiTitle` invocando `changeState(UiMainMenu)`. Mapeamento interativo do teclado e controle via `cellPad` ativado via `PAD_AUTOPRESS=1` e polling direto no Windows.
- **Status:** **Em evolução**.

---

### 5. [MONITORADO] Sincronização de SPU Jobs e Labels RSX

- **Sintoma:** Possível bloqueio na sincronização de pós-processamento SPU com RSX (NID `0x7FDF4FEF`).
- **Investigação:** O projeto atual possui 11 workloads SPU mapeados e 15 jobs JobQueue. A barreira `taskset=0x120F7D00` inicializa com 6 workers sem travas.
- **Status:** **Estável**.
