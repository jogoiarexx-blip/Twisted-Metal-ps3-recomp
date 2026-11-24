# Análise de Engenharia Reversa Automatizada com REA (REA_ANALYSIS.md)

## Visão Geral

Utilizando as ferramentas de engenharia reversa integradas (REA — *Reverse Engineer Anything* — e Ghidra 12.2 PUBLIC instalados no ambiente `D:\infamous recomp`), foi mapeada e analisada a estrutura semântica dos executáveis e tabelas de despacho de *Twisted Metal*.

---

## 1. Mapeamento Semântico da Máquina de Estados da UI Front-End

A tabela virtual central do gerenciador de UI (Front-End Manager / `fe_mgr` em `0x00F42288`) aloca classes de estados derivadas com a assinatura de vtable `0x005CB92C` no slot 4 (`d4`).

| Endereço da Vtable | Classe de Estado | Entry Point `onEnter` | Entry Point `update` | Função no Fluxo de Execução |
|---|---|---|---|---|
| `0x00CEF490` | `UiLegal_HealthWarning` | `0x00475150` | `0x004751D8` | Apresenta o aviso de saúde/epilepsia do PS3 |
| `0x00CEF290` | `UiLegal_1` | `0x00474110` | `0x00474198` | Tela legal inicial da Sony Computer Entertainment |
| `0x00CEF310` | `UiLegal_2` | `0x0047447C` | `0x004744F8` | Tela legal Eat Sleep Play |
| `0x00CEF390` | `UiLegal_3` | `0x00474710` | `0x00474890` | Tela legal Dolby Digital / Áudio |
| `0x00CEF410` | `UiLegal_4` | `0x00474A68` | `0x00474BF0` | Tela legal de marcas registradas |
| `0x00CEF4E8` / `0x00CEF510` | `UiLegal_ESRB` | `0x00475450` | - | Classificação indicativa ESRB (US) |
| `0x00CF0420` | `UiIntroMovie` | `0x004AA780` | `0x004AAA98` | Reprodução de vídeo de introdução / transição cinematográfica |
| `0x00CEF690` | `UiAttract / UiPreMenu` | `0x0047EC50` | `0x0047F8F8` | Apresentação em loop de atração do jogo |
| `0x00CF0628` | `UiTitle` | `0x004B05A0` | `0x004B0A40` | Tela de título ("Press START") |
| `0x00CEF590` | `UiMainMenu` | `0x00476D34` | `0x0047ADB8` | Menu Principal ("SELECT GAME CATEGORY") |
| `0x00CEF810` | `UiCampaignSelect` | `0x004822E8` | - | Seleção de modo de campanha e veículos |

---

## 2. Assinatura da Lógica de Navegação em `0x0047F8F8` (UiPreMenu)

A rotina de descompressão e verificação do loop de atração consulta:
- String ID `0xCB4`: `"PREV/NEXT"`
- String ID `0xC80`: `"  SELECT"`
- String ID `0x33D`: `"SELECT GAME CATEGORY"`

Ao receber o evento de confirmação de entrada, o despachante avalia os retornos:
- Código 1: Chama `changeState(machine, *(fe_mgr + 0x3ABC))` -> Transição para `UiMainMenu`.
- Código 2: Chama `changeState(machine, *(fe_mgr + 0x3B20))` -> Transição para `UiTitle`.
- Código 3: Chama `changeState(machine, *(fe_mgr + 0x3A28))` -> Transição de seleção secundária.
