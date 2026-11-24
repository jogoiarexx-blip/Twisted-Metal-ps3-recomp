# Twisted Metal (BCUS98106) — Recompilação Estática e Análise PPU/SPU

Este diretório contém os metadados de análise, tabelas de despacho HLE e modelos de subsistemas para a recompilação estática do *Twisted Metal (2012)* para PC.

---

## ⚠️ AVISO IMPORTANTE: `boot_probe.exe` vs `twistedmetal.exe`

* **`boot_probe.exe` (NESTE DIRETÓRIO):**
  É apenas um harness de teste unitário preliminar histórico (v0.5 a v0.19) para validar as primeiras instruções de inicialização de memória e TLS com o ELF de atualização 1.06. **Ele NÃO é o jogo executável.** Ao terminar de testar a alocação de memória, ele encerra intencionalmente.
  > *Nota de compatibilidade:* Foi recompilado com Clang-cl / MSVC nativo para não depender de `libstdc++-6.dll` do MinGW.

* **`twistedmetal.exe` (NA RAIZ DO REPOSITÓRIO):**
  É o **executável real e completo** do jogo, contendo todas as 38.229 funções PPU recompiladas, 11 imagens SPU embutidas, pipeline DirectX 12 RSX funcional e áudio BoomRangBuss.
  > Para rodar o jogo real, use **`INICIAR_TWISTED_METAL.bat`**, **`RODAR-JOGO.cmd`** ou **`run_twistedmetal.ps1`** na pasta raiz.
  > Para verificar o diagnóstico do boot probe, utilize **`VERIFICAR_BOOT.bat`**. As DLLs de runtime (`libstdc++-6.dll`, `libgcc_s_seh-1.dll`, `libwinpthread-1.dll`) estão incluídas na raiz.

---

## 📊 Metadados do Jogo Base (1.00)

O pipeline de recompilação do jogo base utiliza os arquivos de análise presentes nesta pasta:

- **`functions_100.json`**: Mapeamento das 31.032 funções identificadas diretamente a partir das tabelas `.opd` e fluxo de controle do `EBOOT.ELF` do disco.
- **`functions_100_seeded.json`**: Mapeamento expandido para 38.229 funções (47.106 símbolos), cobrindo todos os gaps de código para lifting completo sem pontas soltas.
- **`ppu_hle_nids_100.cpp`**: Tabela de resolução de NIDs de sistema PS3 (chamadas de SO, áudio, rede, vídeo e arquivos) para despacho direto no runtime HLE.
- **`spurs_hle.hpp`**: Modelagem de inicialização de barreiras SPURS (`cellSpursBarrierInitialize` - NID `0x7FDF4FEF`) e consulta de tasksets (`cellSpursGetTasksetInfo` - NID `0x9FCB567B`), essenciais para o pipeline gráfico pós-FX.

---

## 🛠️ Pipeline de Lifting PPU e SPU

1. **Detecção e Seed de Gaps:**
   ```bash
   python ../tools/find_functions.py input/EBOOT.ELF --output functions_100.json
   python ../tools/seed_gaps.py input/EBOOT.ELF functions_100.json -o functions_100_seeded.json
   ```

2. **Extração de SPUs Embutidas:**
   ```bash
   python ../tools/extract_spu_images.py input/EBOOT.ELF --output spu_100
   python ../tools/recarve_spu.py spu_100
   python ../tools/build_spu_workloads.py spu_100 spu_gen_100
   ```

3. **Lifting PPU em Chunks C++:**
   ```bash
   python ../tools/ppu_lifter.py input/EBOOT.ELF \
       --functions functions_100_seeded.json \
       --code-end 0xC79C6C \
       --output src_recomp_100 -j 12
   python ../tools/post_lift.py src_recomp_100
   ```

4. **Compilação do Executável Nativo:**
   A compilação é gerenciada pelo CMake na raiz do repositório:
   ```cmd
   cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang-cl -DCMAKE_C_COMPILER=clang-cl
   cmake --build build
   ```
