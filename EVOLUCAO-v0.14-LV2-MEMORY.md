# Evolução v0.14 — LV2 Memory HLE

**BCUS98106 (atualização 1.06) — protótipo experimental, ainda não jogável.**

## Antes → depois

| Área | v0.13 | v0.14 |
|---|---|---|
| Inicialização PPU | Parada em `0x4EC8EC` | Avança até `0x98C8C0` nos testes locais |
| `sys_memory_get_user_memory_size` (`0x160`) | Identificado, não implementado | HLE parcial no harness |
| `sys_memory_allocate` (`0x15C`) | Identificado, não implementado | Alocação dinâmica de memória guest no harness |
| Região guest | Segmentos iniciais | Janela adicional `0x40000000..0x4FFFFFFF` |
| SPURS | Ponte parcial | Preservada |
| Jogo completo / FPS | Não executável / não medido | Não executável / não medido |

### Implementação local realizada

- Validação dos tamanhos e alinhamentos de páginas.
- Memória do PlayStation representada separadamente dos endereços do processo anfitrião.
- Escrita em formato big-endian.
- Tratamento de falha por falta de memória e parâmetros inválidos.
- Alocação de 15 MB no teste de inicialização.

### Validação

Na preparação da v0.14, **47 verificações novas passaram**, junto a testes de regressão relevantes. O teste diferencial dependente de Unicorn não foi repetido por falta da biblioteca naquele ambiente. Não houve teste de FPS nem renderização 3D.

### Compatibilidade

SHA-256 do EBOOT estudado:
`41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d`

Não misturar offsets com a versão de disco 1.00.

### Próxima prioridade

Recompilar o helper PPU `0x98C8C0` e aprofundar a inicialização, antes de tentar os sistemas de cena, controles e áudio.

**Aviso:** este arquivo documenta o progresso local da v0.14; os arquivos de código-fonte ainda requerem sincronização com este repositório.
