# Render
For render web usages

## Scrape.do Research MCP

Servidor privado para leitura de páginas públicas como Markdown através do scrape.do.
Disponibiliza a ferramenta `scrape_url` pelo endpoint MCP Streamable HTTP `/mcp`.

Configuração e custos: [DEPLOYMENT.md](DEPLOYMENT.md).

### Execução

Requer Python 3.12 e os segredos `SCRAPEDO_TOKEN` e `MCP_AUTH_TOKEN` injetados no ambiente
por um gestor de segredos. O processo recusa arrancar se faltarem ou forem iguais.

```sh
pip install -r requirements.txt
python server.py
```

Não guardar chaves no repositório nem usar o token scrape.do como senha do MCP.
Chamadas autenticadas usam `Authorization: Bearer <segredo MCP>`.
Não colocar credenciais no URL. Não há logging de acesso nem de pedidos HTTP upstream.

### Comportamento

- Só leitura HTTP(S), sem cookies ou credenciais para sites de destino.
- Sem redirecionamentos ou retries automáticos; se necessário usar o URL final.
- Recusa destinos privados/locais e portas não padrão.
- Uma chamada simultânea, até cinco por minuto por processo; resposta até 200 KB.
- Não solicita JavaScript nem proxy residencial. Perfis automáticos do fornecedor
  ainda podem aumentar o custo; créditos efetivos são devolvidos quando disponíveis.
- Conteúdo externo é marcado como dados não fiáveis, nunca instruções.
- Segredos conhecidos são expurgados do corpo; erros upstream são genéricos.
- A resolução DNS local é uma validação preventiva; o fornecedor resolve novamente
  o destino, pelo que não é uma garantia contra todas as formas de DNS rebinding.

### Testes sem consumo da API

```sh
pip install pytest==9.1.1
python -m pytest -q
```

Testes usam credenciais fictícias e transporte HTTP simulado; cobrem autenticação,
negociação MCP, URLs privados, redaction, erros, créditos, tamanho e frequência.
