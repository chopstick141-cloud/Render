# Publicação gratuita aprovada — bloqueada até validar teto de custos

Preparada em 10 de setembro de 2026. Nenhum serviço criado nesta preparação.

## Restrição vinculativa do utilizador — 10/09/2026

O utilizador confirmou a opção gratuita e determinou: nunca ultrapassar os limites.
Não contratar planos pagos, upgrades, recargas nem permitir cobranças de excedentes.
Ao atingir os limites, a integração deve parar até à renovação gratuita da quota.
Antes de publicar, verificar bloqueios efetivos do lado de ambos os fornecedores,
abrangendo compute, tráfego, builds e créditos. Alertas ou limites em memória não
substituem um bloqueio de cobrança. Se não for possível garantir essas condições,
manter a publicação suspensa e reportar a limitação. Não pedir novamente aprovação
para o plano Free; apenas resolver os requisitos de acesso e proteção financeira.

A tentativa de autenticação segura no painel Render terminou com erro de transporte;
o estado de autenticação não foi confirmado. Nenhum serviço foi criado.

## Configuração concreta

- Destino: Daniel's workspace (confirmado pela integração Render).
- Repositório: https://github.com/chopstick141-cloud/Render
- Branch preparada: feat/scrapedo-mcp (rever antes de integrar em main).
- Serviço: scrapedo-research-mcp; runtime Python; região Frankfurt.
- Plano proposto: Free; uma instância; sem base de dados, discos ou cron.
- Build: `pip install -r requirements.txt`
- Start: `python server.py` (escuta 0.0.0.0:$PORT).
- Health check: `/healthz`; MCP Streamable HTTP: `/mcp`.
- Auto-deploy: desativado para permitir revisão de futuras alterações.
- Segredos obrigatórios no Render: `SCRAPEDO_TOKEN` e `MCP_AUTH_TOKEN`.
  Usar valores diferentes; gerar a segunda chave com um gerador criptográfico.
- Definir `PYTHON_VERSION=3.12.12` como variável não secreta.
- O hostname público é obtido da variável automática `RENDER_EXTERNAL_HOSTNAME`.

Não criar o serviço antes de confirmar os custos com o utilizador. A criação via
Render pode iniciar imediatamente o primeiro deploy, mesmo com auto-deploy desligado.
Inserir os segredos apenas pelo mecanismo de segredos/variáveis protegidas do Render;
nunca em commits, ficheiros .env, descrições, logs ou URLs de configuração do cliente.
O cliente recebe apenas o segredo de acesso MCP em `Authorization: Bearer ...`.
O token scrape.do é enviado apenas ao endpoint HTTPS do fornecedor.

## Custos e limites confirmados nas fontes públicas

| Componente | Proposta | Limites |
|---|---|---|
| Render compute | Free, US$0 de compute | 750 horas/workspace/mês; adormece após 15 minutos; despertar cerca de 1 minuto |
| Render tráfego/build | Incluído até aos limites do workspace | Excedentes podem ser cobrados se existir método de pagamento; confirmar Billing antes de publicar |
| Scrape.do Free | US$0/mês; 1.000 créditos | Não foi confirmado o plano nem o saldo da conta autenticada |
| Scrape.do Hobby (não selecionado) | US$29/mês; 250.000 créditos | Exige aprovação separada |

Fontes consultadas em 10/09/2026:
- https://render.com/docs/free
- https://scrape.do/pricing/
- https://scrape.do/documentation/request-costs/

Uma chamada normal tem custo base de 1 crédito, mas o fornecedor pode aplicar
perfis automáticos por domínio (por exemplo, Google: 10). Não prometer 1.000 páginas
por 1.000 créditos. `Scrape.do-Request-Cost` é o valor efetivo devolvido pelo fornecedor.
Sem chamadas reais ao scrape.do durante os testes desta preparação.

O limite local de 5 chamadas/minuto e uma chamada simultânea reduz consumo acidental;
reinicia com o processo e NÃO constitui um teto mensal de despesa. Para custo zero,
confirmar o plano Free do scrape.do e as condições de excedentes no Billing do Render.
O total da conta Render pode incluir custos do plano de workspace, não consultados
pela ferramenta de listagem de serviços.

## Verificação depois da aprovação

1. Confirmar Billing, plano scrape.do e acesso seguro aos segredos.
2. Integrar a alteração revista e criar o serviço com as definições acima.
3. Confirmar deploy live, saúde HTTP 200 e MCP sem credenciais HTTP 401.
4. Testar initialize e tools/list com credenciais; depois uma chamada real autorizada.
5. Confirmar créditos consumidos e configurar o cliente MCP compatível.

Hospedar o servidor não o instala automaticamente em todos os chats. O cliente
precisa de suportar Streamable HTTP com header Bearer e de uma configuração própria.
Este projeto não implementa OAuth; clientes que exijam OAuth precisam dessa etapa
adicional. Não remover autenticação como alternativa.
