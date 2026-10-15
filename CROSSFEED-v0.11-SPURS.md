# Twisted Metal BCUS98106 **update 1.06** — crossfeed SPURS v0.11

## Correção cruzada implementada

A análise do outro port do mesmo jogo (ELF de disco, revisão diferente) apontou
as duas funções do pós-processamento `cellSpursBarrierInitialize` (NID
`0x7FDF4FEF`) e `cellSpursGetTasksetInfo` (`0x9FCB567B`). Elas estão no mapa
de importações **da nossa revisão 1.06** nos endereços `0xC8C02C` e
`0xC8C144`, respectivamente, e constam implementadas no ps3recomp 0.14.0.

O dispatcher local da v0.11 agora suporta estes NIDs usando o modelo `Memory`
big-endian, com campos da barreira e do taskset compatíveis com a representação
do runtime 0.14.0. Não retorna sucesso sem preencher as estruturas e preserva
os códigos de erro negativos no ABI PowerPC64. Outros NIDs não implementados
continuam falhando explicitamente.

`recomp/spurs_hle_test.cpp` valida 16 verificações de argumentos, layout,
status, alinhamento, limites de memória e dispatcher. Compile e execute:

```sh
cd recomp
g++ -std=c++17 -O2 -Wall -Wextra -Werror spurs_hle_test.cpp -o spurs_hle_test
./spurs_hle_test
```

**Limite importante:** não é integração completa do runtime. A inicialização
ainda para no endereço `0x4EC8D0`, e as chamadas SPURS ficam prontas apenas
para quando o código PPU avançar até elas. Não foram testados SPU scheduler,
RSX, FPS ou jogabilidade. Não combinar com o código recompilado do outro ELF.

Base técnica: ps3recomp 0.14.0, `libs/spurs/cellSpurs.c`,
`libs/spurs/spurs_taskset.h` (MIT, detalhes no arquivo LICENSE).
