# Twisted Metal v0.15 — continuação do heap PPU

**Base:** BCUS98106, EBOOT associado à atualização 1.06. Este repositório contém somente ferramentas, código reimplementado e testes; **não contém o jogo**.

## Resultado

O teste local com o EBOOT do usuário evoluiu do ponto `0x98C8C0` (v0.14) até a **próxima chamada pendente em `0x988AA8`**. É uma continuação do *boot harness*, **não uma inicialização completa nem um executável jogável**.

## Novas rotinas

- `heap_start_0098c8c0`: prólogo PPC64, frame de 176 bytes e preservação dos registradores não voláteis.
- `heap_helper_00988b78`: inicialização do descritor global, máscara/limite do pool e interrupção explícita no caminho de erro.
- `heap_after_00988b78`: verifica tamanho, capacidade e alinhamento; prepara os argumentos para `0x98769C`.
- `heap_memset_0098769c`: HLE limitada ao intervalo guest mapeado, sem acesso aos dados host fora do mapeamento.
- `heap_after_0098769c`: grava os metadados da arena.
- `heap_list_heads_00988b0c`: inicializa os 32 cabeçalhos da lista duplamente encadeada.
- `heap_after_00988b0c`: prepara a chamada seguinte, `0x988AA8`, e retorna o PC em vez de inventar uma resposta.
- `heap_failed_return_0098c9f8`: epílogo da saída antecipada.

A origem dos endereços foi conferida por desassemblagem do EBOOT. O verificador `recomp/verify_heap_init.py` confere hash SHA-256 do EBOOT e de dois trechos críticos antes da reprodução.

## Testes efetuados localmente

- `heap_init_test.cpp`: inicialização global, argumentos ABI, memset, listas, ramos de erro e recuperação de stack — aprovado.
- `boot_probe` com EBOOT 1.06: chegou a `0x988AA8` — aprovado.
- Regressões: 47 verificações LV2, 16 SPURS, 16 `startup3`, 7 `startup4` — aprovadas.
- Sanitizadores AddressSanitizer/UndefinedBehaviorSanitizer no teste de heap — aprovados.
- GitHub Actions compila os testes e o boot probe sem o ELF original. Isso **não substitui** o teste local com o EBOOT.

## Reproduzir com seu próprio EBOOT

```bash
cd recomp
python3 verify_heap_init.py /caminho/EBOOT.elf
g++ -std=c++17 -O2 -Wall -Wextra -Werror heap_init.cpp heap_init_test.cpp -o heap_init_test
./heap_init_test
g++ -std=c++17 -O2 -Wall -Wextra -Werror entry.cpp startup2.cpp startup3.cpp startup4.cpp heap_init.cpp boot_probe.cpp -o boot_probe
./boot_probe /caminho/EBOOT.elf
```

No Windows, `recomp/COMPILAR-WINDOWS.cmd` compila o boot probe com Visual Studio ou MinGW e aceita o EBOOT como argumento.

## Pendências

1. Traduzir/verificar `0x988AA8` e as chamadas restantes do inicializador do heap.
2. Validar eventos de alocação/liberação e evitar atalhos que mascaram falhas.
3. Prosseguir até a execução das tarefas SPU, RSX e apresentação de gráficos.
4. Só medir FPS e resposta de controles quando houver uma cena reproduzível.

A variante de ELF **1.00 (disco)**, o ps3recomp e o RPCS3 permanecem separados. Não misturar offsets entre versões. Não foi comprovada nenhuma melhoria de FPS.
