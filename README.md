# Red Team Lab

Laboratório educacional de reconhecimento controlado para estudos de
Segurança da Informação e operações Red Team autorizadas.

## Funcionalidades

- Verificação de portas TCP no loopback IPv4.
- Rejeição de alvos que não sejam endereços de loopback.
- Validação de portas entre 1 e 65535.
- Identificação de serviços prováveis por número de porta.
- Identificação HTTP básica em portas TCP abertas.
- Coleta do status HTTP e do cabeçalho Server.
- Relatórios JSON com data, alvo e resultados.
- Testes automatizados com unittest e mocks.

## Requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa para o módulo atual.

## Execução

Verificar as portas padrão:

    python -m src.recon.port_check

Escolher as portas:

    python -m src.recon.port_check --ports 22,80,8000,8080

O alvo padrão é 127.0.0.1. Outros endereços são rejeitados.

## Identificação HTTP

Quando uma porta TCP está aberta, o laboratório tenta obter informações
HTTP básicas usando uma requisição HEAD.

São registrados:
- Status HTTP.
- Cabeçalho Server, quando disponível.
- Erros de comunicação ou respostas não reconhecidas.

A consulta HTTP é restrita ao endereço 127.0.0.1.

## Testes

Executar com pytest:

    python -m pytest -q

Ou com unittest:

    python -m unittest discover -s tests -v

## Relatórios

O relatório é salvo em reports/port-check.json.
Os relatórios gerados localmente não são enviados ao Git.

## Limitações

- Verifica apenas conexões TCP.
- A identificação de serviço pelo número da porta é apenas uma indicação.
- O cabeçalho Server pode estar ausente ou ser impreciso.
- A identificação HTTP não comprova a identidade real do serviço.
- "closed_or_filtered" não diferencia porta fechada de filtrada.
- Os testes de portas abertas, fechadas e respostas HTTP usam mocks.
- Não é uma ferramenta completa de varredura ou exploração.

Utilize somente sistemas próprios ou com autorização explícita.
