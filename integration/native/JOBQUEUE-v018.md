# v0.18 — SPURS JobQueue: verificação e lifting dos 15 módulos

## O que foi confirmado no upstream

O registro [sp00nznet/twistedmetal: src/gen/spu_jobs.c](https://github.com/sp00nznet/twistedmetal/blob/main/src/gen/spu_jobs.c) referencia 15 jobs SPURS JobQueue, diferentes dos SPUs embutidos no EBOOT. O runtime [ps3recomp](https://github.com/sp00nznet/ps3recomp/blob/ydkj-master-bringup/runtime/spu/spu_workload.c) salva cada job desconhecido via variável de ambiente SPU_DUMP_MISS em arquivos com nome spujob_<FNV-hex16>_<tamanho>.bin.

O hash usa o offset 1469598103934665603 e a constante 1099511628211 usados no código original. Não substituir pelo offset FNV convencional.

## Novas ferramentas

- prepare_jobqueue.py confere os 15 fingerprints do registro, a integridade dos dumps locais, limites de 256 KiB, alinhamento, nomes e tamanhos.
- Por padrão não inicia lifting se faltarem módulos ou houver arquivo inválido. --check só verifica; --plan mostra os comandos sem executar.
- Executa find_spu_functions.py com --raw --base 0 para os jobs em formato binário cru; em seguida spu_lifter.py com funções explícitas e prefixo único job_HASH_.
- Normaliza os includes do runtime e exige definições reais de funções levantadas (não aceita só prototypes).
- Gera fontes apenas em twistedmetal/src/spu_gen/job_HASH/ e um manifesto local com SHA-256 de cada entrada e código levantado.
- doctor.py agora rejeita manifesto incompleto, ausente ou adulterado quando o registro dos 15 jobs está ativo. Nada é enviado ao GitHub.

## Capturando os dumps

Somente uma execução real **do runtime nativo do ps3recomp**, chegando ao envio dos jobs, pode produzir os dumps via SPU_DUMP_MISS. Isso não é uma opção padrão do RPCS3. Com uma versão nativa de captura já compilada, no PowerShell:

~~~powershell
New-Item -ItemType Directory -Force C:\TM2012\job-dumps
$env:SPU_DUMP_MISS = 'C:\TM2012\job-dumps'
& 'C:\TM2012\twistedmetal\build\twistedmetal.exe' 'C:\TM2012\twistedmetal\input\EBOOT.ELF'
Remove-Item Env:\SPU_DUMP_MISS
~~~

**Bloqueio real:** ainda não existe uma build de captura comprovada no repositório do usuário. A versão completa do upstream não pode ser ligada sem esses jobs. Para a primeira captura será preciso preparar um build temporário de diagnóstico que omita o registro JobQueue até os dumps existirem, restaurando-o depois; sessões parciais talvez não produzam todos os 15 jobs. Esta versão NÃO automatiza o bootstrap inicial. Os dois ZIPs públicos não fornecem os dumps.

## Conferir e levantar localmente depois da captura

Na pasta C:\TM2012, com o upstream, runtime, EBOOT original 1.00 e seus 15 dumps:

~~~powershell
py .\meu-recomp\integration\native\prepare_jobqueue.py --upstream .\twistedmetal --runtime .\ps3recomp --dumps .\job-dumps --check
py .\meu-recomp\integration\native\prepare_jobqueue.py --upstream .\twistedmetal --runtime .\ps3recomp --dumps .\job-dumps --plan
py .\meu-recomp\integration\native\prepare_jobqueue.py --upstream .\twistedmetal --runtime .\ps3recomp --dumps .\job-dumps
py .\meu-recomp\integration\native\doctor.py --upstream .\twistedmetal --runtime .\ps3recomp --eboot .\twistedmetal\input\EBOOT.ELF --strict
~~~

Não renomear arquivos para forçar hashes. O verificador compara FNV com os bytes, impedindo associações falsas. Só use build_windows.py da v0.16 após todos os pré-requisitos estarem satisfeitos.

## Testes e limites

Os testes da CI são sintéticos, incluindo fingerprints, fontes fictícias com execução simulada e SHA-256 de manifesto. **Nenhum dump comercial, código PPU/SPU derivado do EBOOT, EBOOT original, EXE do jogo ou chave foi publicado.** Sucesso desses testes não comprova boot, menu, gráficos 3D, controles ou gameplay. A pesquisa v0.15 com ELF candidato à atualização 1.06 permanece separada.
