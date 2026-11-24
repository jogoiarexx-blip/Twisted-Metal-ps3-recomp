# Roteiro Técnico e Marcos de Evolução (ROADMAP.md)

Este documento estabelece o plano de marcos técnicos (M01 a M18) para a entrega da versão nativa autônoma de *Twisted Metal (2012)* no Windows.

---

## 1. Marcos de Evolução

- **M01 — Build Reproduzível:** ✅ **CONCLUÍDO**
  - Compilação modular completa via `clang-cl` + Ninja + CMake 3.20+.
  - 12 compilações modulares de PPU gerando `twistedmetal.exe`.

- **M02 — Boot Nativo Estável:** ✅ **CONCLUÍDO**
  - Inicialização de CRT, TLS (0x10F00000), descritores OPD e heap guest.
  - Carregamento de PRXs estáticos e despacho de entry point `0x00F030D0`.

- **M03 — Vídeos e Transições:** ✅ **CONCLUÍDO**
  - Carregamento de arquivos `.psarc` e `.rtt`.
  - Tratamento de `MoviePlayer` e auto-skip cinematográfico seguro.
  - Carrossel de telas legais (`UiLegal_HealthWarning` a `UiLegal_4`).

- **M04 — Tela Inicial Correta:** ✅ **CONCLUÍDO**
  - Inicialização do Front-End Manager (`fe_mgr`).
  - Entrada em `UiAttract / UiPreMenu` e `UiTitle` ("Press START").

- **M05 — Menu Principal Interativo:** ✅ **CONCLUÍDO / EM VALIDAÇÃO**
  - Acesso verificado à vtable `0x00CEF590` e exibição de `"SELECT GAME CATEGORY"`.
  - Captura periódica de superfícies D3D12 (`surf_menu_*.ppm`).

- **M06 — Seleção de Veículos:** 🔄 **PRÓXIMO MARCO**
  - Implementação do ciclo de navegação em `UiCampaignSelect` (`0x00CEF810`).
  - Carregamento dos modelos de veículos (`cars/crimson/crm_prot.rtt`, `cars/grim/grm_prot.rtt`, etc.).

- **M07 — Carregamento de Mapas:** 📋 Planejado
  - Despacho de `WorldLoader::loadGame` para arenas de combate (`mplevels/arena`, `mplevels/rooftops`).

- **M08 — Renderização do Cenário:** 📋 Planejado
  - Pipeline de malhas de mundo e texturas difusas / normais de terreno.

- **M09 — Renderização dos Veículos:** 📋 Planejado
  - Renderização dos carros e partes destacáveis (chassi, armas).

- **M10 — Controles e Movimentação:** 📋 Planejado
  - Mapeamento analógico contínuo de direção, aceleração e frenagem.

- **M11 — Física e Colisões:** 📋 Planejado
  - Integração do motor de física in-engine (destruição de cenários e impactos).

- **M12 — Armas e Combate:** 📋 Planejado
  - Disparo de mísseis, metralhadoras e especiais.

- **M13 — Inteligência Artificial:** 📋 Planejado
  - Navegação de bots e detecção de alvos.

- **M14 — Áudio e Efeitos:** 📋 Planejado
  - Reprodução em tempo real de amostras de áudio e músicas do banco BoomRangBuss.

- **M15 — Primeira Partida Completa:** 📋 Planejado
  - Conclusão de uma rodada completa de combate com vitória/derrota.

- **M16 — Campanha Jogável:** 📋 Planejado
  - Progressão através dos capítulos da história (Sweet Tooth, Mr. Grimm, Dollface).

- **M17 — Otimização e Estabilidade:** 📋 Planejado
  - Redução de tempo de carregamento e estabilização de 60 FPS travados.

- **M18 — Versão Nativa Distribuível:** 📋 Planejado
  - Pacote standalone sem arquivos proprietários embutidos, pronto para distribuição limpa.
