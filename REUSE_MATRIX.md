# Matriz de Reutilização de Projetos Externos (REUSE_MATRIX.md)

Este documento avalia e classifica a interoperabilidade técnica e a procedência legal do código de projetos externos de recompilação do ecossistema PS3.

---

## 1. Classificação Metodológica

- **Reaproveitamento Direto:** Módulos ou scripts que podem ser utilizados sem alteração substancial de arquitetura.
- **Reaproveitamento com Adaptação:** Módulos cujo design ou rotina lógica é compatível, mas necessita de ajuste para o executável ou motor específico (TMX / ESP).
- **Referência Arquitetural:** Documentação, padrões comportamentais ou fluxos de execução adotados como modelo conceitual sem cópia direta de código.
- **Incompatível:** Recursos específicos de outros motores gráficos ou sob licenças que colidem com a política de distribuição limpa do projeto.

---

## 2. Matriz Comparativa

| Projeto / Repositório | Licença | Classificação | Área de Aplicação | Avaliação Técnica |
|---|---|---|---|---|
| **sp00nznet/twistedmetal** | MIT | **Reaproveitamento Direto** | Pipeline, SPU & FIOS | Base primária da extração de 11 imagens SPU, scripts de reparo pós-lifter (`post_lift.py`), e HLE de `sys_ppu_thread_once` para destravamento do FIOS. |
| **sp00nznet/ps3recomp** | MIT | **Reaproveitamento Direto** | Runtime PPU / SPU | Branch `ydkj-master-bringup` contendo o runtime C++ nativo e dispatch NID 64-bit. |
| **andrebrumdev/gow2-recomp** | MIT | **Reaproveitamento com Adaptação** | D3D12 RSX & Shaders | Técnicas de ciclo de vida de alvos de renderização e sincronização de buffers duplos com apresentação D3D12. |
| **sethlikepie/Gow2HD-Windows** | MIT | **Referência Arquitetural** | Build & Automação | Estrutura de automação de testes de integração contínua e tratamento de exceptions vetoriais no Windows. |
| **whompay/inFAMOUSreborn** & **aphixe/infamousRebornUsa** | MIT | **Reaproveitamento com Adaptação** | SPURS & D3D12 Fences | Políticas de retenção de memória de recursos de GPU até a confirmação da fence D3D12 (`0013-d3d12-resources-fence`). |
| **RPCS3/rpcs3** | GPLv2 | **Referência Arquitetural** | Validação & Comportamento | **Não há cópia de código.** O RPCS3 é utilizado estritamente como oráculo de comportamento para comparação de traces, buffers de áudio e NIDs não documentados. |
| **InfraCode-Dev/rea** & **dmore/rea** | MIT | **Reaproveitamento Direto** | Engenharia Reversa | Ferramental de engenharia reversa automatizada com Ghidra 12.2 para mapeamento semântico de tabelas virtuais e rotinas de UI. |
| **Ascension-R / Soleanna** | MIT | **Referência Arquitetural** | SPU Lifter & Cache | Padrões de expansão de cache SPU de 8 para 64 entradas e descompressão DEFLATE rápida em threads nativas. |

---

## 3. Conformidade e Licenciamento

Todo o código incorporado respeita as licenças de código aberto correspondentes (MIT/Apache 2.0). Nenhuma biblioteca proprietária da Sony (Sony Computer Entertainment SDK / PRX proprietários) ou código restrito sob GPLv2 com vinculação estática ao executável foi copiado sem separação de domínio.
