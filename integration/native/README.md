> **v0.18:** comandos para verificar e levantar os 15 jobs SPURS a partir de dumps locais, sem gerar funções fictícias: [JOBQUEUE-v018.md](JOBQUEUE-v018.md). A primeira compilação/captura ainda precisa ser reproduzida no Windows.

# v0.16 — Compilação nativa Windows (alvo PS3 1.00)

Esta etapa cria uma ponte **independente** para [sp00nznet/twistedmetal](https://github.com/sp00nznet/twistedmetal); não substitui o boot probe v0.15 do nosso ELF candidato 1.06. Os endereços e TOCs são diferentes. O [FranklinCG](https://github.com/franklincg/twisted-metal-2012-ps3-native-port) fornece testes de estruturas e não um jogo recompilado.

## Ferramentas incluídas

- doctor.py: verifica SHA-256 do EBOOT, host Windows, CMake/Ninja/clang-cl, checkouts, runtime e arquivos PPU/SPU gerados. Não altera arquivos.
- build_windows.py: só chama o CMake do upstream se o diagnóstico estiver completo e o hash for do disco 1.00. Com a opção --run tenta iniciar o EXE local.
- test_native.py: testes unitários sintéticos no GitHub Actions.

Nenhum EBOOT, ISO, PSARC, chave, ativo proprietário, código levantado do jogo nem binário do game está incluído.

## Preparação (Windows)

Instale Visual Studio 2022 C++ e use Developer PowerShell for VS 2022; requer Git, Python 3.9+, CMake 3.20+, Ninja e clang-cl.

~~~powershell
mkdir C:\TM2012
cd C:\TM2012
git clone https://github.com/jogoiarexx-blip/Twisted-Metal-ps3-recomp.git meu-recomp
git clone https://github.com/sp00nznet/twistedmetal.git twistedmetal
git clone --branch ydkj-master-bringup https://github.com/sp00nznet/ps3recomp.git ps3recomp
cmake -S .\ps3recomp -B .\ps3recomp\build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang-cl -DCMAKE_CXX_COMPILER=clang-cl
cmake --build .\ps3recomp\build --target ps3recomp_runtime
~~~

**Atenção:** os ZIPs públicos NÃO incluem os ~295 MB de PPU compilado, ~19 MB de SPU levantado e o runtime precompilado. É necessário gerar localmente a partir da sua própria cópia lícita do **disco 1.00** (não reutilize os endereços do ELF 1.06). Siga o [guia do upstream para análise/lifting](https://github.com/sp00nznet/twistedmetal#reproducing-the-analysis) e confirme os caminhos: twistedmetal/src/recomp/*.cpp, twistedmetal/src/recomp/ppu_recomp.h e twistedmetal/src/spu_gen/**/*.c.

Faça o diagnóstico **antes** de compilar:

~~~powershell
py .\meu-recomp\integration\native\doctor.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot "C:\SeuJogo\PS3_GAME\USRDIR\EBOOT.ELF" --strict
~~~

Quando todas as dependências estiverem presentes:

~~~powershell
py .\meu-recomp\integration\native\build_windows.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot "C:\SeuJogo\PS3_GAME\USRDIR\EBOOT.ELF"
~~~

Para **tentar** executar o binário gerado:

~~~powershell
py .\meu-recomp\integration\native\build_windows.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot "C:\SeuJogo\PS3_GAME\USRDIR\EBOOT.ELF" --run
~~~

O jogo original precisa estar acessível pelo VFS (PS3_GAME/USRDIR); a variável PS3_VFS_ROOT pode ser necessária. Não publique EBOOT, recursos comerciais nem chaves. Use uma instância por teste.

## O que isso NÃO significa

Passar no diagnóstico ou no CMake não comprova que o jogo abre. O upstream documenta bloqueios em SPURS/post-FX, NIDs 0x7FDF4FEF e 0x9FCB567B, geometria e sincronização RSX. [Relatório técnico de partida](https://github.com/sp00nznet/twistedmetal/blob/main/docs/in-match.md). GitHub Pages não executa aplicativos Windows/D3D12.

Próximo marco: obter resultado JSON do doctor, gerar o lifting completo com a cópia local, compilar um Windows EXE, analisar logs reais até frames 3D e controles.
