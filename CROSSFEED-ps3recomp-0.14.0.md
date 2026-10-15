# Twisted Metal v0.9 × ps3recomp 0.14.0 — auditoria de integração

## Evidências
- Hash EBOOT: `41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d`; concordância com manifest: **True**.
- Importações: **583** em **35** módulos.
- Nomes de importação únicos (não hexadecimais): **488**.
- Nomes localizados nos fontes do runtime ps3recomp: **341**. Nomes ausentes: **147**. Isto **não** mede compatibilidade funcional.
- O dispatcher da v0.9 implementa um caso explícito de `sys_initialize_tls_main` e falha nos demais casos. Nomes iguais nos fontes não tornam tais HLE automaticamente disponíveis ao port.

## Principal ganho potencial do ps3recomp 0.14.0
- Changelog registra correção de SPU-to-SPU task signals que evitava espera de até 1 segundo; o próprio changelog menciona quadro de pós-processamento do Twisted Metal com 4,1 segundos antes da correção. **Ainda não integrado neste port.**
- Melhorias Vulkan: targets RGBA16F, stencil, cache/readbacks, superfície e render passes; relevantes a efeitos gráficos, não substituem a compilação PPU/SPU.
- `RSX_ENGINE_PASS_DUMP` e `PS3RECOMP_VK_DUMP_EVERY` ajudam a depurar rendering.
- Ferramentas `ppu_loader.py`, `ppu_lifter.py`, `gen_hle_nids.py`, `spu_lifter.py` fornecem pipeline mais amplo do que os blocos traduzidos manualmente em v0.9.

## Barreiras reais / prioridade
1. Executar `ppu_loader.py` no ELF e reconciliar OPD/TOC/imports com a tabela do port (endereços de importação podem divergir em formato).
2. Gerar e compilar um subconjunto PPU com o lifter de 0.14.0, comparando comportamento ao bloco de inicialização v0.9.
3. Unificar a ABI de memória, CPU e o encaminhamento NID/HLE; **não** copiar arquivos do runtime sem adaptação.
4. Extrair imagens SPU e habilitar SPURS/sinais; testar pós-processamento depois de boot real.
5. Integrar GCM/RSX e Vulkan/D3D12 para renderização e medir frametimes reais.

## Verificações que esta entrega NÃO comprova
- Jogo inicializável ou FPS melhorado.
- Código ps3recomp 0.14.0 compilado junto com o port.
- APIs homônimas funcionando corretamente.
- RPCS3 configurado ou acelerado: é uma via separada.

## Módulos mais frequentes
- `sysPrxForUser`: 143
- `cellSpurs`: 55
- `sceNp`: 52
- `cellGcmSys`: 44
- `cellSysutil`: 38
- `sys_fs`: 27
- `sys_net`: 24
- `sceNpTus`: 19
- `cellSpursJq`: 16
- `cellFont`: 16
- `cellVoice`: 15
- `sys_io`: 12
- `cellNetCtl`: 12
- `sceNpTrophy`: 11
- `cellAudio`: 11
