# v0.17 — Reprodução local do lifting PPU e SPU (BCUS98106 1.00)

Agora existe um pipeline local que executa os scripts reais do [ps3recomp](https://github.com/sp00nznet/ps3recomp/tree/ydkj-master-bringup) contra seu próprio ELF **do disco 1.00**. Não há código comercial levantado, EBOOT ou chaves no GitHub. O boot probe v0.15 do ELF candidato a atualização 1.06 fica separado.

## Etapas automáticas

- ppu_loader.py cria o mapa de entrada e as importações.
- find_functions.py cria meta/functions.json.
- extract_spu_images.py encontra SPUs embutidos no EBOOT local.
- A rotina de recarving confere o tamanho dos SPUs com a mesma regra do runtime.
- ppu_lifter.py levanta o PPU usando o TOC 0xF21930, code-end 0xC79C6C e os stubs HLE da imagem 1.00.
- post_lift.py aplica os patches idempotentes **da versão 1.00**, apenas após validar o SHA-256 do ELF.
- build_spu_workloads.py levanta os SPUs **embutidos** e registra os workloads no runtime.

As fontes geradas ficam somente no checkout local twistedmetal, sob src/recomp e src/spu_gen. A opção --plan mostra os comandos sem executar nada. Por segurança, --overwrite é necessário para refazer um lift existente.

## Uso no Windows

Siga primeiro [o README da preparação do Windows](README.md). Abra Developer PowerShell for VS 2022, instale as dependências indicadas nos projetos e deixe os três repositórios clonados em C:\TM2012.

Para inspecionar o plano, sem ler o ELF:

~~~powershell
py .\meu-recomp\integration\native\prepare_lift.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot ".\twistedmetal\input\EBOOT.ELF" --jobs 8 --plan
~~~

Para executar a geração real usando **seu EBOOT.ELF decifrado legalmente do disco 1.00**:

~~~powershell
py .\meu-recomp\integration\native\prepare_lift.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot ".\twistedmetal\input\EBOOT.ELF" --jobs 8
~~~

O comando recusa arquivos desconhecidos e não tenta decifrar ou baixar jogos.

Depois execute o diagnóstico completo:

~~~powershell
py .\meu-recomp\integration\native\doctor.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot ".\twistedmetal\input\EBOOT.ELF" --strict
~~~

## Bloqueio de SPURS JobQueue ainda existente

O arquivo [src/gen/spu_jobs.c do upstream](https://github.com/sp00nznet/twistedmetal/blob/main/src/gen/spu_jobs.c) referencia **15 módulos SPURS JobQueue capturados durante execução**, independentes dos 11 SPUs embutidos no EBOOT. Por isso o novo diagnóstico confere se esses símbolos realmente existem nos fontes SPU levantados. Sem esses módulos o link pode falhar, mesmo que o PPU e os SPUs embutidos sejam gerados.

Esses jobs precisam ser recuperados da **sua própria execução local da mesma versão 1.00**, convertidos em fontes com o lifter SPU, e vinculados ao executável. Não criar implementações vazias para forçar o linker a passar. Consulte [análise de partida e SPURS upstream](https://github.com/sp00nznet/twistedmetal/blob/main/docs/in-match.md).

## Limites verificados

A GitHub Actions valida apenas a sequência de comandos, proteção do SHA-256, prevenção de sobrescrita e cobertura de símbolos com dados sintéticos. Isso **não** equivale a gerar PPU ou SPU verdadeiros, compilar o jogo completo ou demonstrar gameplay. O Windows EXE e a renderização 3D permanecem pendentes de um teste com os arquivos locais do usuário. Relatórios ficam sob twistedmetal/meta (não subir ao GitHub). O GitHub Pages não roda executáveis Windows.
